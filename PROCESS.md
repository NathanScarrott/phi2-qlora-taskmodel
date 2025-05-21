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

### Fine-Tuning
- 

### Quantization
- 

### API Development
- 

## Challenges & Solutions
- 

## References
- 