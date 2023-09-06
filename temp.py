data1 = '''
{

"abnormalities": {

"Biparietal Diameter (BPD)": "10.65 pctl",

"Abdominal Circumference (AC)": "fetal growth restriction Abdominal Circumference(AC) < 10th percentile"

}

}'''

data2 = '''
{

"abnormalities": {

"Fetal Position": "Shoulder presentation",

"Placenta Location": "Low-lying"

}

}'''
import json


# # Merge the dictionaries
# merged_dict = {**data1_dict, **data2_dict}

# # Convert the merged dictionary back to JSON
# merged_json = json.dumps(merged_dict, indent=4)

# # Print the merged JSON
# print(merged_json)
data1 = json.loads(data1)
data2 = json.loads(data2)
data1["abnormalities"].update(data2["abnormalities"])
print(data1)

# input_data = {
#     "person": {
#         "name": "Jane Smith",
#         "age": 25,
#         "address": {
#             "street": "123 Main St",
#             "city": "Los Angeles"
#         }
#     }
# }

# output_data = flatten_json(input_data)
# # output_data = remove_empty_keys(output_data)
# # output_json = json.dumps(output_data)
# print(output_data)


# Example JSON data
# json_str = '''
# {
#   "data": {
#     "id": 123,
#     "name": "Product",
#     "categories": [
#       {
#         "id": 1,
#         "name": "Category A",
#         "subcategories": [
#           {
#             "id": 11,
#             "name": "Subcategory A1"
#           },
#           {
#             "id": 12,
#             "name": "Subcategory A2"
#           }
#         ]
#       },
#       {
#         "id": 2,
#         "name": "Category B",
#         "subcategories": [
#           {
#             "id": 21,
#             "name": "Subcategory B1"
#           },
#           {
#             "id": 22,
#             "name": "Subcategory B2"
#           }
#         ]
#       }
#     ]
#   }
# }

# '''
