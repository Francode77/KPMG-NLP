# Function to extract a summary from a file
# This function needs pytorch and ml6team/mbart-large-cc25-cnn-dailymail-nl-finetune!

def get_abstr_summary(document_id,language):
    import os

    text_file=f'{language}_{document_id}.txt'
    text_file_path=os.path.join('..','processed_data',language,text_file)
    try:
        with open (text_file_path,encoding="UTF-8") as f:
            text=f.read()
    except:
        text_file=f'{document_id}.txt'
        text_file_path=os.path.join('..','processed_data',language,text_file)

        with open (text_file_path,encoding="UTF-8") as f:
            text=f.read()

    import transformers

    undisputed_best_model = transformers.MBartForConditionalGeneration.from_pretrained(
        "ml6team/mbart-large-cc25-cnn-dailymail-nl-finetune"
    )
    tokenizer = transformers.AutoTokenizer.from_pretrained("facebook/mbart-large-cc25")
    summarization_pipeline = transformers.pipeline(
        task="summarization",
        model=undisputed_best_model,
        tokenizer=tokenizer,
    )
    summarization_pipeline.model.config.decoder_start_token_id = tokenizer.lang_code_to_id[
        "nl_XX"
    ]
    summarization_pipeline.save_pretrained("summarizer")

    text  # Dutch
    summary=summarization_pipeline(
        text,
        do_sample=True,
        top_p=0.75,
        top_k=50,
        # num_beams=4,
        min_length=100,
        early_stopping=True,
        truncation=True,
    )[0]["summary_text"] 


    return summary