import requests

# Configuration
url = "http://localhost:8000/infer"
prompts_file = "prompts.txt"
results_file = "results.txt"

def read_prompts(file_path):
    with open(file_path, 'r') as file:
        prompts = [line.strip() for line in file if line.strip()]
    return prompts

def send_inference_request(prompt):
    # payload = {
    #     "sentence": prompt
    # }
    response = requests.post(url, params={"sentence": prompt}, timeout=180)
    return response.json()

def main():
    prompts = read_prompts(prompts_file)
    
    with open(results_file, 'w') as file:
        for i, prompt in enumerate(prompts):
            result = send_inference_request(prompt)
            file.write(f"Prompt {i+1}: {prompt}\n")
            file.write(f"Response: {result}\n\n")
            print(f"Processed prompt {i+1}")

if __name__ == "__main__":
    main()
