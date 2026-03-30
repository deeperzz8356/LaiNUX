import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="f:/LaiNUX/agentic_os/.env")
api_key = os.getenv("GOOGLE_API_KEY")


def list_models_with_genai_sdk(key: str):
    """Preferred path using the newer google-genai SDK."""
    try:
        from google import genai
    except Exception as exc:
        raise RuntimeError(f"google-genai import failed: {exc}")

    client = genai.Client(api_key=key)
    names = []
    for model in client.models.list():
        model_name = getattr(model, "name", None) or str(model)
        names.append(model_name)
    return names


def list_models_with_legacy_sdk(key: str):
    """Fallback path for older environments using google-generativeai."""
    try:
        import google.generativeai as legacy_genai
    except Exception as exc:
        raise RuntimeError(f"google-generativeai import failed: {exc}")

    legacy_genai.configure(api_key=key)
    names = []
    for model in legacy_genai.list_models():
        model_name = getattr(model, "name", None) or str(model)
        names.append(model_name)
    return names


def main():
    if not api_key:
        print("Error: GOOGLE_API_KEY is not set. Add it to agentic_os/.env")
        return

    try:
        models = list_models_with_genai_sdk(api_key)
        source = "google-genai"
    except Exception as first_error:
        try:
            models = list_models_with_legacy_sdk(api_key)
            source = "google-generativeai (legacy)"
        except Exception as second_error:
            print("Error: unable to list models with either SDK")
            print(f" - New SDK failure: {first_error}")
            print(f" - Legacy SDK failure: {second_error}")
            return

    print(f"Available models (via {source}):")
    for model_name in models:
        print(f" - {model_name}")


if __name__ == "__main__":
    main()
