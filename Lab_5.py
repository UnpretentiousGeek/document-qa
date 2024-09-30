import requests
import streamlit as st
import json
from openai import OpenAI

system_message = """
Don't make assumptions about what values to plug into functions. 
Ask for clarification if a user request is ambiguous.
"""

if 'client' not in st.session_state:
    api_key = st.secrets['openai_key']
    st.session_state.client = OpenAI(api_key=api_key)

def get_current_weather(location, format):

    if "," in location:

        location = location.split(",")[0].strip()


    urlbase = "https://api.openweathermap.org/data/2.5/"
    urlweather = f"weather?q={location}&appid={st.secrets['weather_key']}"
    url = urlbase + urlweather


    response = requests.get(url)
    data = response.json()


    # Extract temperature values in Kelvin
    temp_kelvin = data['main']['temp']
    feels_like_kelvin = data['main']['feels_like']
    temp_min_kelvin = data['main']['temp_min']
    temp_max_kelvin = data['main']['temp_max']
    humidity = data['main']['humidity']

    # Convert temperatures based on the unit argument
    if format == 'celsius':
        temp = temp_kelvin - 273.15
        feels_like = feels_like_kelvin - 273.15
        temp_min = temp_min_kelvin - 273.15
        temp_max = temp_max_kelvin - 273.15
    elif format == 'fahrenheit':
        temp = (temp_kelvin - 273.15) * 9/5 + 32
        feels_like = (feels_like_kelvin - 273.15) * 9/5 + 32
        temp_min = (temp_min_kelvin - 273.15) * 9/5 + 32
        temp_max = (temp_max_kelvin - 273.15) * 9/5 + 32
    else:
        raise ValueError("Invalid unit. Please choose either 'celsius' or 'fahrenheit'.")

    # Return the weather information in the desired unit
    return {
        "location": location,
        "temperature": round(temp, 2),
        "feels_like": round(feels_like, 2),
        "temp_min": round(temp_min, 2),
        "temp_max": round(temp_max, 2),
        "humidity": round(humidity, 2),
        "unit": format
    }




tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "format": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "The temperature unit to use. Infer this from the users location.",
                    },
                },
                "required": ["location", "format"],
            },
        }
    }]

if "messages" not in st.session_state:
    st.session_state["messages"] = \
    [{"role": "system", "content":system_message},
        {"role": "assistant", "content": "Ask Something?"}]

for msg in st.session_state.messages:
    if msg["role"] != "system":    
        chat_msg = st.chat_message(msg["role"])
        chat_msg.write(msg["content"])

openai_client = st.session_state.client

if prompt := st.chat_input("Ask about weather"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    response = openai_client.chat.completions.create(
        model='gpt-4o-mini', 
        messages=st.session_state.messages, 
        tools= tools, 
        tool_choice="auto",
    )
    response_message = response.choices[0].message
    st.session_state.messages.append({"role": "assistant", "content": response_message.content})
    st.write(response_message.content)
    tool_calls = response_message.tool_calls
    if tool_calls:
        
        tool_call_id = tool_calls[0].id
        tool_function_name = tool_calls[0].function.name
        arguments = json.loads(tool_calls[0].function.arguments)

        if tool_function_name == 'get_current_weather':
            results = get_current_weather(arguments['location'], arguments['format'])
            st.session_state.messages.append({
                "role":"tool", 
                "tool_call_id":tool_call_id, 
                "name": tool_function_name, 
                "content":json.dumps(results)
            })
            
            model_response_with_function_call = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=st.session_state.messages,
                stream= True
            )
            with st.chat_message("assistant"):
                model_response_with_function_call = st.write_stream(model_response_with_function_call)

            st.session_state.messages.append({"role": "assistant", "content": model_response_with_function_call})
        else: 
            st.write(f"Error: function {tool_function_name} does not exist")
    else: 
        with st.chat_message("assistant"):
            response = st.write_stream(response)

        





