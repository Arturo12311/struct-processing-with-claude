# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

#BATCHING
def batch_data(data, token_limit=100000):
    """
    breaks the data into batches based on the specified token limit
    """
    batches_dict = {}
    count = 1
    batch = ""
    tokens = 0

    for key, value in data.items():
        item = json.dumps({key: value}, indent=2)
        if tokens + len(item) // 4 > token_limit:
            batches_dict[count] = batch
            count += 1; batch = ""; tokens = 0
        else:
            tokens += len(item) // 4
            batch += item + ",\n"
    
    if batch != "":
        batches_dict[count] = batch

    return batches_dict


#ASSEMBLE MESSAGE
def assemble_message(batch_data):
    """
    Returns a list of messges ready to send to claude 
    """   
    instructions = """
    I am going to send you a batch of data that should be in json format.
    Your task is to simplify all the field values based on the provided simplify criteria.
    Dont include any extra text.
    Ensure its proper Json format
    Dont forget the comma at the end of the last structure in the batch.
    dont add a newline between structures, keep it jsut like the provided example format

    Example output format:
    "SendChatMessageRequest": {
        "Base": "FTzErTozMessage",
        "ChatKind": "ETzChatKindType",
        "InfoToShare": "s",
        "Text": "s"
    },
    "CheatOpenFogResponse": {
        "Base": "FTzErTozMessageWithResultCode",
        "FogCuid": "I"
    },
    "CraftResultInfo": {
        "CraftRewardCuid": "I",
        "CraftResultKind": "ETzCraftResultKindType",
        "ItemInfo": "msg"
        "CraftGreatSuccessBonusKind": "ETzCraftGreatSuccessBonusKindType"
        "GearQuality": "ETzGearQualityType",
        "Amount": "i"
    },

    simplify criteria:
        - use a simple python struct format string whenever applicable.
            in-scope: "(([1-9]\d*)?[cbB?hHiIlLqQfds])+"
        - wrap maps, arrays, and sets in []. preserve and classify the inner types. 
            format for maps: ["map_key", "map_value"] 
            format for arrays: ["array_type"]
            for nested maps and arrays apply this format recursively. example:
            ["map_key", ["map_key", "map_value"]]
            ["map_key", ["map_key", ["map_key", "map_value"]]]
            ["map_key", ["array_type"]]
        - for structs and enums just store the name as the value. if the struct name doesnt start with FTz or enum name doesnt start wit ETz, prepend the prefix.
        struct: "FTzstructname", enum: "ETzenumname"
        - Tshared ptr is either a struct or a map, clasiffy it accordingly.
            if TSharedPtr<FTz... treat as a struct 
            if TSharedPtr<TMap... treat as a map
        - for messages put "msg" as the field value
        - for bools put "?" as the field value
        - classify strings and Fstrings as "s"

    Heres the legend for custom types: 
        - FDateTime: "IQ"
        - FGuid: "I2H8B"
        - FIntVector2D: "2I"
        - FRotator: "3f"
        - FVector: "3f"
        - FTimespan: "2f"
        - FVector2D: "2f"
        - Fstring: "s"
        - Cuid: "I"
        - Vuid: "Iq"

    additionaly context:
        - fields with just a struct should just be in ""
        - always use double quotes
        - ignore nullability
        - The arrays and maps are uncleaned strings extracted from the decompiled code. Focus on the inner data types for classification. Ignore irrellevant info such as: "TSizedDefaultAllocator<32>>,void". 
        - If I didnt specify it as a custom type, Treat it as its native type.
        - Dont focus on spelling mistakes in class and structnames.
        - never wrap the outer square brackets for maps and arrays in quotes. 
        - wrap all individual simplified types in quotes. Example: ["FTzGetLocationInfo"], ["I", "ETzGetLocationInfo"], "i", "3f"
        - treat base structs as regular structs. 
        
    examples: 
        1.Map with inner struct type
        "AnniversaryAchievementInfos": {
            "type": "map",
            "value": "<TMap<FTzCuid,TArray<TSharedPtr<FTzAnniversaryAchievementInfo,(ESPMode)1>,TSizedDefaultAllocator<32>>,FDefaultSetAllocator,TDefaultMapHashableKeyFuncs<FTzCuid,TArray<TSharedPtr<FTzAnniversaryAchievementInfo,(ESPMode)1>,TSizedDefaultAllocator<32>>,false>",
            "nullable": false}
        simplified: 
            "AnniversaryAchievementInfos": ["I", ["FTzAnniversaryAchievementInfo"]]
        2. array of struct type
        "ItemIndexWithCounts": {
            "type": "array",
            "value": "<TArray<TSharedPtr<FTzItemIndexWithCount,(ESPMode)1>,TSizedDefaultAllocator<32>>,void>",
            "nullable": false}
        simplified: 
            "ItemIndexWithCounts": ["FTzItemIndexWithCount"]
        3. map with inner struct type 
        "CovenantBattalionInfos": {
            "type": "map",
            "value": "<TMap<long_long,TSharedPtr<FTzCovenantBattalionNotifyInfo,(ESPMode)1>,FDefaultSetAllocator,TDefaultMapHashableKeyFuncs<long_long,TSharedPtr<FTzCovenantBattalionNotifyInfo,(ESPMode)1>,false>",
            "nullable": false}
        simplified: 
            "CovenantBattalionInfos": ["q", "FTzCovenantBattalionNotifyInfo"]
        4. enum field
        "AdjustKind": {
            "type": "enum",
            "value": "ETzMissionAdjustKindType",
            "nullable": false
        },
        simplified: 
            "AdjustKind": "ETzMissionAdjustKindType"
        5. enum without ETz prepended
        "AdjustKind": {
            "type": "enum",
            "value": "MissionAdjustKindType",
            "nullable": false
        },
        simplified: 
            "AdjustKind": "ETzMissionAdjustKindType"
        6. struct 
        "Base": {
            "type": "struct",
            "value": "ErTozMessageWithResultCode",
            "nullable": false
        },
        simplififed:    
            "Base": "FTzErTozMessageWithResultCode"
        7. message type
        "ItemInfo": {
            "type": "message",
            "value": null,
            "nullable": false
        },
        simplified:
            "ItemInfo": "msg"
        8. Fstring type
        "Text": {
            "type": "custom",
            "value": "FString",
            "nullable": false
        }
        simplified:
            "Text": "s"
    """
    
    message = [
        {"role": "user", "content": instructions},
        {"role": "assistant", "content": "Ok Got it! Send me the data to process!"},
        {"role": "user", "content": batch_data},
    ]
    return message

   
#SEND MESSAGE
def send_message(message):
    """
    sends message to claude and return the response
    """
    import anthropic
    client = anthropic.Anthropic(
        api_key="",
        default_headers={"anthropic-beta": "max-tokens-3-5-sonnet-2024-07-15"})
    
    response = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=8192,
        temperature=0.1,
        system="Your world-class reverse engineer with a specialization in simplifying parsing structures",
        messages = message,
    )
    return response


#SAVE RESPONSE
def save_response(content, file):
    """
    append to output file
    """
    with open(file, 'a') as f:
        f.write("\n")
        f.write(content)
    
    return True


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 


import json

INPUT_FILEPATH = '_structures.json'
OUTPUT_FILEPATH = '_claude_structures.json'
with open(INPUT_FILEPATH, 'r') as file:
    data = json.load(file)


def main():
    """
    make claude clean the structures and save the results
    """
    batches = batch_data(data, token_limit=11000)
    print(len(batches))
    for key, value in batches.items():
        if key == 1: continue
        print("\n-----------------------")
        print(f"Processing batch: {key}...")

        message = assemble_message(value)
        response = send_message(message)

        saved = save_response(response.content[0].text, OUTPUT_FILEPATH)
        if not saved:
            print(f"Error saving batch{key}")
            break

        if response.stop_reason != "end_turn":
            print(f"Error encountered while processing batch {key}")
            break

        print(f"SUCCESS! \nAppended Claude's response to \"{OUTPUT_FILEPATH}\" for batch: {key}")
        print(f"Input tokens: {response.usage.input_tokens}")
        print(f"Output tokens: {response.usage.output_tokens}")
    
    print("\n-----------")
    print(f"FINISHED")
    print(f"PROCESSED ALL {len(batches)} to {OUTPUT_FILEPATH}")




main()
