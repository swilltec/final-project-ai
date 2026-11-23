from transformers import pipeline, set_seed
from utils import RESULTS, record


def main() -> None:
    """Run the sentiment, fill-mask, and text-generation examples on CPU."""
    RESULTS.mkdir(exist_ok=True)
    set_seed(42)
    output = RESULTS / "exercise_1.txt"

    with output.open("w", encoding="utf-8") as log:
        record("=== Sentiment analysis ===", log)
        classifier = pipeline(
            "sentiment-analysis",
            model="distilbert/distilbert-base-uncased-finetuned-sst-2-english",
            device=-1,
        )
        # The last example is deliberately sarcastic; confidence is not a measure
        # of whether the classifier understood the intended meaning.
        sentences = [
            "The lecture made a difficult topic surprisingly clear.",
            "The application crashed and I lost my work.",
            "Great, another two-hour meeting that could have been an email.",
        ]
        for sentence in sentences:
            result = classifier(sentence)[0]
            record(
                f"Input: {sentence}\nPrediction: {result['label']}; "
                f"confidence: {result['score']:.4f}\n",
                log,
            )

        record("=== Fill-mask ===", log)
        # RoBERTa uses <mask> as its placeholder and returns ranked predictions.
        unmasker = pipeline("fill-mask", model="FacebookAI/roberta-base", device=-1)
        sentences = [
            "The chef stirred the soup with a <mask>.",
            "The astronaut looked at Earth from the <mask>.",
        ]
        for sentence in sentences:
            record(f"Input: {sentence}", log)
            for prediction in unmasker(sentence, top_k=3):
                record(
                    f"  {prediction['token_str'].strip()}: "
                    f"{prediction['score']:.4f} — {prediction['sequence']}",
                    log,
                )

        record("\n=== Text generation ===", log)
        generator = pipeline(
            "text-generation", model="openai-community/gpt2", device=-1
        )
        prompts = [
            "A robot entered the library and",
            "The best way to learn a new skill is",
        ]
        for prompt in prompts:
            record(f"\nPrompt: {prompt}", log)
            continuations = generator(
                prompt,
                max_new_tokens=40,
                num_return_sequences=2,
                do_sample=True,
                pad_token_id=generator.tokenizer.eos_token_id,
            )
            for number, result in enumerate(continuations, 1):
                record(f"Continuation {number}: {result['generated_text']}", log)

    print(f"\nSaved to {output}. Review the results for your written comparison.")


if __name__ == "__main__":
    main()
