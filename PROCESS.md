# PHI-2 QLoRA Development Process

## Timeline

| Date | Phase | Notes |
|------|-------|-------|
|      | Setup |       |
|      | Data Generation |       |
|      | Fine-Tuning |       |
|      | Quantization |       |
|      | API Development |       |
|      | Testing |       |

## Notes

### Setup
21/05/25 18:30
Set-up went smoothly :D. Now let's get down to business.

### Data Generation
#### Defining the Task
21/05/25 18:50
So I need to define the task for an LLM to generate our data. For this I need to know what the format of the data should be and what kind of things I should generate. I know I'm going to try use google/gemini-2.5-flash-preview - good performance, specialises in mass output and cheap as hell! ($0.15/$0.6 I/O per 1M tokens) Let me first look into how I should structure the data.

21/05/25 19:25

Ok I've set up a file (/data/generate_dataset.py). It uses the LLM to generate N amount of example inputs and outputs. Due to the nature of what this fine-tuned LLM will be applied to, the input is just a request such as "What is the weather in [CITY] and the output is a JSON structure which can be processed for us to access API such as weather API, todoist and gmail.

21/05/25 19:30
I ran a sample test with 10 JSON outputs. I am looking for many different types of requests such as email, weather and adding tasks to todo list. It produced 9/10 todo list JSONs. This is because I provide only 1 seed JSON example (which is todo list oriented). I will now provide all 3 types.

21/05/25 19:40
Ok, even with all 3 examples the model is still baising the get-weather intent quite heavily. I think this is because it's the easiest. I will just specifcy the intent in each one instead by continuously iterating through ["add_task", "get_weather", "send_email"].

21/05/25 19:50
Ok all done on that. Also added some rate limit handling for the API just in case. Think it's solid now. Leaving it for the night, Spurs Europa league final. COYS.

---

24/05/25 10:40
Ok, I'm on the train working now. I am looking to generate my training dataset of 1000 examples. Actually, I might do 1200. I know there is something about needing to split into training and testing so I want to make sure I have enough for training. I think 1000 training, 200 testing should be fine. I'll look into this more.

I've updated the code to generate the dataset 100 at a time with checkpoints. Should allow me to see the process is going smoothly without having to spend the money/time waiting to check the full 1200 are correct all at once. 

24/05/25 11:10
I've generated 1/3 of the dataset. I think it all looks good. I have 2 concerns. It uses punctuation often, which will not be the case when doing speech to text. The other, smaller concern, is that the data is maybe not quite variant enough. It does vary a fair amount but ideally I want it a bit more. I'll keep this data but adjust the prompt/temperature to adjust these issues for the next 900.

24/05/25 11:25
Ok I was wrong about the captilisation and punctation in the above entry. I am using whisper by openai (the python package). It does punctuate and capitalize everything.

24/05/25 11:40
I've generated about 800 data points. I will do the rest now but the data looks good from what I can tell. I guess we will see how effective it is when I actually fine tune the model with it. Anyway, after this is done I will fine tune the model to behave how I want it to do. This will be done in Google Colab since I dont feel like waiting 1-3 days for it to be fine tuned on my laptop's hardware ':D.

### Fine-Tuning
03/06/25 16:25
I'm going to fine-tune the model now. Need to look into this more before I do it.

03/06/25 16:40 
I've just uploaded the dataset and split into training and testing. Next bit is setting up the Environment for fine-tuing.

04/05/2025 13:00 
Ok I fine-tuned the model with 3 epochs. I am now going to test if this has been effecive. It's jsut taking me AGES to pull the adapter_model.safetensors file from github in Starbucks - 650KB/s :(
    
04/05/2025 13:20
I pulled it now but also have to also download the base phi-2 model so we can apply our LoRA weights - which is 5GB. I will do this when home. I also made a file to test this with 3 basic requests.

04/05/2025 15:05
Ok I've fine-tuned it and it seems to be working pretty well. One issue is that it doesnt know when to stop but it's ok, I just extract any valid JSON. Happy with results, maybe I could fine tune more in future so that it knows when to stop but for now it's fine.

04/05/2025 20:05
Ok the final step is to merge my LoRA adapter with the basse model to get my merged model. Doing that now.
### Quantization

04/05/2025 20:20
Ok so quantizing the model was really easy and the model still seems to be working really well. It has took the time it takes to run from 90 secs to 2.5 which is really nice. 

I guess the next step is hooking it upto Fast API. I've not had loads of experience with this so it should be good.

### API Development

04/05/2025 20:40
Ok, also hooking it up to FastAPI was fairly easy. Although I said I hadn't had much experience it was quite similar to the experience I have had. I like FastAPI - it's quick and easy.

04/05/2025 20:45
Hit Git LFS quota exceeded error trying to push 5GB+ model files. Nuclear option - nuked .git directory, created proper .gitignore, force pushed clean 582KB repo with just the essential code. It was getting very messy and I couldn't figure it out. Think I messed it up earlier - lesson learnt.

04/05/2025 21:00
Now looking to put it on AWS EKS instance.

### AWS EKS Deployment

04/05/2025 21:15
Set up AWS account, IAM user, billing alerts. Created EKS cluster with t3.medium spot instances. Took ages to create (~20 mins) but worked first time.

04/05/2025 21:45
Had to containerize with Docker first. Created Dockerfile + requirements-docker.txt. Initially failed building because llama-cpp-python needed Git - added git/cmake to apt-get install and it worked.

04/05/2025 22:00
Pushed to ECR, deployed to Kubernetes. Pod kept crashing - platform mismatch! Built for ARM64 but EKS nodes are x86_64. Rebuilt with --platform linux/amd64.

04/05/2025 22:15
Working but SLOW - 68 seconds per request vs 2.5s local ':D. t3.medium CPU-only vs my M1 Pro.

04/05/2025 22:30
Tomorrow will try ARM64 instances (m6g.large) for better performance. Deleted whole cluster - saves ~£1/day and fresh start.

### Voice Assistant Integration

05/05/2025 10:35
Hooked up my FastAPI endpoint to my voice assistant! Replaced the OpenRouter/Gemini intent classification with my fine-tuned Phi-2 model. Working perfectly :D. 

The full pipeline is now: Voice → Whisper → My Phi-2 model → Actions (Todoist, weather, etc). Pretty cool to have the whole thing running with my own model instead of external APIs. Response time is good locally and the intent classification is spot on.

I might see if I can make the TTS local instead of through Eleven Labs API.

## Challenges & Solutions
- 

## References
- 