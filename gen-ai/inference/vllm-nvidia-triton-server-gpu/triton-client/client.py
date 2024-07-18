import argparse
import asyncio
import json
import sys
import time
from os import system

import numpy as np
import tritonclient.grpc.aio as grpcclient
from tritonclient.utils import *


def count_tokens(text):
    return len(text.split())


def create_request(prompt, stream, request_id, sampling_parameters, model_name, send_parameters_as_tensor=True):
    inputs = []
    prompt_data = np.array([prompt.encode("utf-8")], dtype=np.object_)
    try:
        inputs.append(grpcclient.InferInput("PROMPT", [1], "BYTES"))
        inputs[-1].set_data_from_numpy(prompt_data)
    except Exception as e:
        print(f"Encountered an error {e}")

    stream_data = np.array([stream], dtype=bool)
    inputs.append(grpcclient.InferInput("STREAM", [1], "BOOL"))
    inputs[-1].set_data_from_numpy(stream_data)

    if send_parameters_as_tensor:
        sampling_parameters_data = np.array(
            [json.dumps(sampling_parameters).encode("utf-8")], dtype=np.object_
        )
        inputs.append(grpcclient.InferInput("SAMPLING_PARAMETERS", [1], "BYTES"))
        inputs[-1].set_data_from_numpy(sampling_parameters_data)

    outputs = []
    outputs.append(grpcclient.InferRequestedOutput("TEXT"))

    return {
        "model_name": model_name,
        "inputs": inputs,
        "outputs": outputs,
        "request_id": str(request_id),
        "parameters": sampling_parameters
    }


async def main(FLAGS):
    sampling_parameters = {"temperature": "0.01", "top_p": "1.0", "top_k": 20, "max_tokens": 512}
    stream = FLAGS.streaming_mode
    model_name = FLAGS.model_name
    with open(FLAGS.input_prompts, "r") as file:
        print(f"Loading inputs from `{FLAGS.input_prompts}`...")
        prompts = file.readlines()

    results_dict = {}
    total_time_sec = 0  # Initialize total time in seconds

    async with grpcclient.InferenceServerClient(
            url=FLAGS.url, verbose=FLAGS.verbose
    ) as triton_client:
        async def async_request_iterator():
            try:
                for iter in range(FLAGS.iterations):
                    for i, prompt in enumerate(prompts):
                        prompt_id = FLAGS.offset + (len(prompts) * iter) + i
                        results_dict[str(prompt_id)] = {}
                        SYSTEM_PROMPT = """<<SYS>>\nKeep short answers of no more than 100 sentences.\n<</SYS>>\n\n"""
                        full_prompt = "<s>[INST]" + SYSTEM_PROMPT + prompt + "[/INST]"
                        yield create_request(
                            full_prompt, stream, prompt_id, sampling_parameters, model_name
                        )
            except Exception as error:
                print(f"caught error in request iterator: {error}")

        try:
            start_time = time.time()  # Record the start time
            response_iterator = triton_client.stream_infer(
                inputs_iterator=async_request_iterator(),
                stream_timeout=FLAGS.stream_timeout,
            )
            async for response in response_iterator:
                request_start_time = time.time()  # Time when request is sent
                result, error = response
                response_receive_time = time.time()  # Time when response is received

                if error:
                    print(f"Encountered error while processing: {error}")
                else:
                    output = result.as_numpy("TEXT")
                    prompt_id = result.get_response().id
                    prompt = prompts[int(prompt_id) % len(prompts)]
                    input_token_count = count_tokens(prompt)

                    for i in output:
                        output_text = i.decode('utf-8')
                        output_token_count = count_tokens(output_text)
                        end_time = time.time()  # Record the end time

                        end_to_end_latency = response_receive_time - start_time
                        # token_throughput_per_sec = output_token_count / end_to_end_latency if end_to_end_latency != 0 else 0

                        results_dict[prompt_id] = {
                            "Prompt": prompt,
                            "Input Tokens": input_token_count,
                            "Output Tokens": output_token_count,
                            "End-to-End Latency": end_to_end_latency,
                            # "Token Throughput per Second": token_throughput_per_sec,
                            "Response": output_text,
                        }

                        print(f"Model {FLAGS.model_name} - Request {prompt_id}: {end_to_end_latency:.2f} seconds, Input Tokens: {input_token_count}, Output Tokens: {output_token_count}")

        except InferenceServerException as error:
            print(error)
            sys.exit(1)

    with open(FLAGS.results_file, "w") as file:
        for key, val in results_dict.items():
            file.write(
                f"Prompt: {val['Prompt']}\n"
                f"Input Tokens: {val['Input Tokens']}\n"
                f"Output Tokens: {val['Output Tokens']}\n"
                f"End-to-End Latency: {val['End-to-End Latency']}\n"
                f"Response: {val['Response']}")
            file.write("\n=========\n\n")
        print(f"Storing results into `{FLAGS.results_file}`...")

    if FLAGS.verbose:
        print(f"\nContents of `{FLAGS.results_file}` ===>")
        system(f"cat {FLAGS.results_file}")

    total_time_ms = total_time_sec * 1000  # Convert total time to milliseconds
    print(f"Total time for all requests: {total_time_sec:.2f} seconds ({total_time_ms:.2f} ms)")
    print("PASS: vLLM example")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        required=False,
        default=False,
        help="Enable verbose output",
    )
    parser.add_argument(
        "-u",
        "--url",
        type=str,
        required=False,
        default="localhost:8001",
        help="Inference server URL and it gRPC port. Default is localhost:8001.",
    )
    parser.add_argument(
        "-t",
        "--stream-timeout",
        type=float,
        required=False,
        default=None,
        help="Stream timeout in seconds. Default is None.",
    )
    parser.add_argument(
        "--offset",
        type=int,
        required=False,
        default=0,
        help="Add offset to request IDs used",
    )
    parser.add_argument(
        "--input-prompts",
        type=str,
        required=False,
        default="prompts.txt",
        help="Text file with input prompts",
    )
    parser.add_argument(
        "--results-file",
        type=str,
        required=False,
        default="results.txt",
        help="The file with output results",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        required=False,
        default=1,
        help="Number of iterations through the prompts file",
    )
    parser.add_argument(
        "-s",
        "--streaming-mode",
        action="store_true",
        required=False,
        default=False,
        help="Enable streaming mode",
    )
    parser.add_argument(
        "--model-name",
        type=str,
        required=True,
        help="Name of the model to test",
    )
    FLAGS = parser.parse_args()
    asyncio.run(main(FLAGS))
