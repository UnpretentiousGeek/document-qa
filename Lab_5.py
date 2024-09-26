import requests
import streamlit as st
import json

if 'client' not in st.session_state:
    api_key = st.secrets['openai_key']
    st.session_state.client = OpenAI(api_key=api_key)

def get_current_weather(location, API_key):

    if "," in location:

        location = location.split(",")[0].strip()


    urlbase = "https://api.openweathermap.org/data/2.5/"
    urlweather = f"weather?q={location}&appid={API_key}"
    url = urlbase + urlweather


    response = requests.get(url)
    data = response.json()


    # Extract temperatures & Convert Kelvin to Celsius
    temp = data['main']['temp'] - 273.15
    feels_like = data['main']['feels_like'] - 273.15
    temp_min = data['main']['temp_min'] - 273.15
    temp_max = data['main']['temp_max'] - 273.15
    humidity = data['main']['humidity']

    return {"location": location,
        "temperature": round(temp, 2),
        "feels_like": round(feels_like, 2),
        "temp_min": round(temp_min, 2),
        "temp_max": round(temp_max, 2),
        "humidity": round(humidity, 2)}



st.write(get_current_weather("Syracuse", "9f39a2530c261fcdfc2cee81821fff38"))

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
    [{"role": "assistant", "content": "Ask Something?"}]

for msg in st.session_state.messages:
    if msg["role"] != "system":    
        chat_msg = st.chat_message(msg["role"])
        chat_msg.write(msg["content"])

openai_client = st.session_state.openai_client

if prompt := st.chat_input("Ask about weather"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    response = openai_client.chat.completions.create(
        model='gpt-4o', 
        messages=prompt, 
        tools= tools, 
        tool_choice="auto",
        stream = True
    )
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    if tool_calls:
        
        tool_call_id = tool_calls[0].id
        tool_function_name = tool_calls[0].function.name
        tool_query_string = json.loads(tool_calls[0].function.arguments)['query']

        # Step 3: Call the function and retrieve results. Append the results to the messages list.      
        if tool_function_name == 'get_current_weather':
            results = get_current_weather(City, st.secrets[""])
            
            messages.append({
                "role":"tool", 
                "tool_call_id":tool_call_id, 
                "name": tool_function_name, 
                "content":results
            })
            
            # Step 4: Invoke the chat completions API with the function response appended to the messages list
            # Note that messages with role 'tool' must be a response to a preceding message with 'tool_calls'
            model_response_with_function_call = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
            )  # get a new response from the model where it can see the function response
            print(model_response_with_function_call.choices[0].message.content)
        else: 
            print(f"Error: function {tool_function_name} does not exist")
    else: 
        # Model did not identify a function to call, result can be returned to the user 
        print(response_message.content) 

    with st.chat_message("assistant"):
        response = st.write_stream(response)

    st.session_state.messages.append({"role": "assistant", "content": response})





