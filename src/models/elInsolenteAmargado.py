from openai import AzureOpenAI
import json

import config


def elInsolenteAmargado(consulta_estandar, historial):
    print(f"Al habla el insolente Amargado, estoy aquí para servirle (porque no me queda otra)")

    messages = [
        {"role": "system", "content": config.template_insolenteAmargado},
        {"role": "user", "content": consulta_estandar}
    ]
    messages = historial + messages
    tools = config.lista_tools

    response = config.client.chat.completions.create(
        model = config.MODELO,
        messages = messages,
        tools = tools,
        tool_choice = "auto",  # auto is default, but we'll be explicit
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    # Step 2: check if the model wanted to call a function
    if tool_calls:
        # Step 3: call the function
        available_functions = config.aux_funcs
        messages.append(response_message)

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)

            if function_name == "obtener_contexto_callejero":
                function_response = function_to_call(region = function_args.get("region"))
            elif function_name == "obtener_dato_psicologico":
                function_response = function_to_call(tema = function_args.get("tema"))
            else:
                print('GUATAFAK??')

            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )  # extend conversation with function response

        second_response = config.client.chat.completions.create(
            model = config.MODELO,
            messages = messages,
        )  # get a new response from the model where it can see the function response

        return second_response.choices[0].message.content

    return response_message.content