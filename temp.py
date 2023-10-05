import openai
import os

openai.api_key = os.environ.get("OPENAI_API_KEY")

prompt = """
Your Task is to create JSON file of abnormalities.

Strictly Remember the following Knowledge when determining whether a specific parameter is Normal OR Abnormal.
[Fetal HR avg value]:
Normal Fetal HR avg value : 120 bpm to 160 bpm
Abnormal Fetal HR avg value :  Less than 120 bpm or greater than 160 bpm

[AFI cm value]:
If the AFI cm value is between 4.99 cm and 24.99 cm, consider it as normal.
 If the AFI cm value is less than 4.99 cm or greater than 24.99 cm, classify it as abnormal.

[AFI pctl value]:
AFI pctl value Normal range : 4.99 pctl to 94.99 pctl
AFI pctl value Abnormal range : Less than the 4.99 ptcl or greater than the 94.99 ptcl

[Fetal Position]:
Normal <Fetal positions> are only Head down (vertex), Anterior and Posterior
Abnormal <Fetal positions> are  Transverse, Shoulder Presentation and Head up (breech)

[Placenta Location]:
Normal placenta location are Anterior, Posterior, Fundal
Abnormal placenta location are Placenta Previa,vasa previa,Accreta,Percreta,Marginal and Low-lying, 

[Placenta Grade]:
Placenta Grade less than or equal to 2 is considered as normal
Placenta Grade 3 or more considered as abnormal

[Amniotic Fluid]:
Normal : 'Adequate' or 'Normal'
Abnormal : 'Low', 'High', 'Oligohydramnios' and 'Polyhydramnios'

[Fetal Movements]:
Normal values of Fetal Movements are Regular, frequent Or 2
Abnormal values of Fetal Movements are Decreased, Absent, Hyperactive Or less than or equal to 1

[Amniotic Fluid Volume]:
if <Amniotic Fluid Volume> values are Normal,Adequate Or 2 classify them as Normal
if <Amniotic Fluid Volume> values are 'Low', 'High', 'Oligohydramnios', 'Polyhydramnios' Or less than or equal to 1 classify them as Abnormal

Here is the ultrasound Report
{"Exam Date": "08-25-2023", "Age": "22yri0m", "LMP(EDD)": "11-27-2022", "EstabDD": "09-03-2023", "EDD": "09-03-2023", "GA(EDD)": "38w5d", "Fetal HR avg value": "136", "AFI cm value": "17.69", "AFI pctl value": "78.44", "Gender": "Female", "Fetal Position": "Vertex", "Placenta Location": "Anterior", "Placenta Grade": "2", "Amniotic Fluid": "Normal", "Fetal Movements": "0", "Amniotic Fluid Volume": "2", "Q1 avg value in cm": "3.00", "Q2 avg value in cm": "8.12", "Q3 avg value in cm": "6.57", "Q4 avg value in cm": "0.00", "Comment": "\\r\\n       BPP\\r\\n\\r\\n          Single vertex female fetus.\\r\\n        FHR=136bpm with normal cardiac rhythm.\\r\\n        AFI=17.7cm\\r\\n         Anterior placenta grade 2\\r\\n         BPP2/8. No breathing  moving or tone.\\r\\n\\r\\n       KS."}

"""

step2 = """
    create list of abnormalities
    [compulsory json output formate]
            {
                "abnormalities": { } //list of abnormalities Ex. "<parameter>" : "<Normal OR Abnormal>","<parameter>" : "<Normal OR Abnormal>",...
            }
    [thought_chain]
        populate "<parameter>" : "<Normal OR Abnormal>" if any abnormalities in the report and return only json.    
    """
def get_completion(prompt, model="gpt-3.5-turbo"):
    # messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=prompt,
        temperature=0.4  # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]


history = [{"role": "system", "content": prompt}]
history += [{"role": "user", "content": str(step2)}]
response3 = get_completion(history)
print(response3)