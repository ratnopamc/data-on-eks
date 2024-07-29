import asyncio
import aiohttp
import json

# Configuration
url = "http://localhost:8000/infer"
prompts_file = "prompts.txt"
results_file = "results_async.txt"

def read_prompts(file_path):
    with open(file_path, 'r') as file:
        prompts = [line.strip() for line in file if line.strip()]
    return prompts

async def send_inference_request(session, prompt):
    payload = {
        "sentence": prompt
    }
    async with session.post(url, params={"sentence": prompt}) as response:
        return await response.json()

async def process_prompts(prompts, batch_size=20):
    results = []
    async with aiohttp.ClientSession() as session:
        for i in range(0, len(prompts), batch_size):
            batch_prompts = prompts[i:i + batch_size]
            tasks = [send_inference_request(session, prompt) for prompt in batch_prompts]
            batch_results = await asyncio.gather(*tasks)
            results.extend(batch_results)
    return results

async def main():
    prompts = read_prompts(prompts_file)
    results = await process_prompts(prompts)
    
    with open(results_file, 'w') as file:
        for i, (prompt, result) in enumerate(zip(prompts, results)):
            file.write(f"Prompt {i+1}: {prompt}\n")
            file.write(f"Response: {json.dumps(result)}\n\n")
            print(f"Processed prompt {i+1}")

if __name__ == "__main__":
    asyncio.run(main())
