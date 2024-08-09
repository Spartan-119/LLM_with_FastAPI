# Ollama custom models

Ollama allows users to create and customize their own language models using a Modelfile. This document provides an overview of custom models and the parameters that can be used to tailor the model's behavior.

For comprehensive information, please refer to the [official Ollama Modelfile documentation](https://github.com/ollama/ollama/blob/main/docs/modelfile.md).

## What are Custom Models?

Custom models in Ollama are created using a Modelfile, which is a blueprint for building and sharing models. It allows you to specify a base model and customize various aspects of its behavior and output.

## Key Components of a Modelfile

1. **FROM** (Required): Specifies the base model to use.
2. **PARAMETER**: Sets runtime parameters for the model.
3. **TEMPLATE**: Defines the full prompt template for the model.
4. **SYSTEM**: Specifies the system message for setting custom behavior.
5. **ADAPTER**: Optionally applies a LoRA adapter to the base model.
6. **LICENSE**: Specifies the legal license for the model.
7. **MESSAGE**: Allows you to provide example conversations to guide the model's responses.

## Customizable Parameters

Users can adjust various parameters to fine-tune the model's performance and output. Here are some key parameters:

| Parameter      | Description                                                | Default |
|----------------|------------------------------------------------------------|---------|
| temperature    | Controls creativity (higher = more creative)               | 0.8     |
| top_k          | Limits token selection to top K options                    | 40      |
| top_p          | Nucleus sampling threshold                                 | 0.9     |
| num_ctx        | Sets the size of the context window                        | 2048    |
| repeat_penalty | Penalizes repetition in generated text                     | 1.1     |
| num_predict    | Maximum number of tokens to predict                        | 128     |
| stop           | Defines stop sequences for text generation                 | N/A     |
| seed           | Sets a random seed for reproducible generation             | 0       |

## Creating a Custom Model

To create a custom model:

1. Create a Modelfile with your desired specifications (like `llms/mod_phi3`).
2. Use the command: `make create-ollama-model model=<model_name>`

## Example Modelfile

```modelfile
FROM llama3
PARAMETER temperature 0.7
PARAMETER num_ctx 4096
SYSTEM You are a helpful AI assistant named UnfoldAI.
```

This example creates a model based on llama3, sets a slightly lower temperature for more focused outputs, increases the context window, and gives the AI a specific identity.
For more detailed information and advanced usage, please consult the official Ollama Modelfile documentation.
