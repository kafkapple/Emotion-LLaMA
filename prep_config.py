import os
import yaml
import re
from pathlib import Path

target_value_to_quote = None

# 사용자 정의 Dumper를 사용하여 특정 키의 값을 큰따옴표로 감싸도록 설정
class CustomDumper(yaml.Dumper):
    def represent_scalar(self, tag, value, style=None):
        # 특정 값에 대해서만 큰따옴표로 감싸기
        if isinstance(value, str) and value == target_value_to_quote:
            style = '"'
        return super().represent_scalar(tag, value, style)
# Path config change based on the place of the script
class ConfigPath:
    def __init__(self):
        model_llama_dir = r"checkpoints\Llama-2-7b-chat-hf"
        target_config_model_path = r"minigpt4\configs\models\minigpt_v2.yaml"

        model_hubert_dir = r"checkpoints\transformer\chinese-hubert-large"
        target_file_conversation_path = r"minigpt4\conversation\conversation.py"

        model_emotion_llama_path = r"checkpoints\save_checkpoint\Emoation_LLaMA.pth"
        target_config_demo_path = r"eval_configs\demo.yaml"

        self.config_paths = [
            {
                "source": model_llama_dir,#"config_model",
                "target": target_config_model_path,
                "keyword": "llama_model"
            },
            {
                "source": model_hubert_dir,
                "target": target_file_conversation_path,
                "keyword": "model_file = "
            },
            {   
                "source": model_emotion_llama_path,
                "target": target_config_demo_path,
                "keyword": "ckpt"
            }
        ]
        print("Init config_paths:\n", self.config_paths)
    @staticmethod
    def replace_after_keyword_py(file_path, keyword, new_value):
        with open(file_path, "r") as f:
            lines = f.readlines()

        modified_lines = []
        for line in lines:
            if keyword in line:
                # 특정 키워드 뒤의 모든 문자열을 새로운 값으로 변경
                # 정규 표현식: 키워드 이후부터 줄 끝까지의 모든 내용을 치환
                pattern = fr'({re.escape(keyword)})(.*)'
                if re.search(pattern, line):
                    modified_line = re.sub(pattern, rf'\1 {new_value}', line)
                    modified_lines.append(modified_line)
                else:
                    # 키워드는 있지만 형식이 맞지 않는 경우는 그대로 추가
                    modified_lines.append(line)
            else:
                # 키워드가 없는 줄은 그대로 추가
                modified_lines.append(line)

        with open(file_path, "w") as f:
            f.writelines(modified_lines)
    # 특정 키워드 뒤의 값을 변경하는 함수 - YAML 파일용
    @staticmethod


    # 특정 키워드 뒤의 값을 변경하는 함수 - YAML 파일용
    def replace_after_keyword_yaml(file_path, key, new_value):
        global target_value_to_quote
        target_value_to_quote = new_value

        with open(file_path, "r") as f:
            yaml_data = yaml.safe_load(f)

        # 재귀적으로 키를 찾고 값 변경하기
        def modify_yaml(data, key, new_value):
            if isinstance(data, dict):
                for k, v in data.items():
                    if k == key:
                        data[k] = new_value  # 값을 직접 할당
                    elif isinstance(v, (dict, list)):
                        modify_yaml(v, key, new_value)
            elif isinstance(data, list):
                for item in data:
                    modify_yaml(item, key, new_value)

        modify_yaml(yaml_data, key, new_value)

        # 파일에 쓰기: 특정 값에만 큰따옴표 추가
        with open(file_path, "w") as f:
            yaml.dump(yaml_data, f, Dumper=CustomDumper, default_flow_style=False, allow_unicode=True)

    # def replace_after_keyword_yaml(file_path, key, new_value):
    #     with open(file_path, "r") as f:
    #         yaml_data = yaml.safe_load(f)

    #     # 재귀적으로 키를 찾고 값 변경하기
    #     def modify_yaml(data, key, new_value):
    #         if isinstance(data, dict):
    #             for k, v in data.items():
    #                 if k == key:
    #                     data[k] = new_value  # 값을 직접 할당 (큰따옴표는 yaml.dump에서 처리)
    #                 elif isinstance(v, (dict, list)):
    #                     modify_yaml(v, key, new_value)
    #         elif isinstance(data, list):
    #             for item in data:
    #                 modify_yaml(item, key, new_value)

    #     modify_yaml(yaml_data, key, new_value)

    #     # 파일에 쓰기: 항상 큰따옴표를 사용하도록 설정
    #     with open(file_path, "w") as f:
    #         yaml.dump(yaml_data, f, default_flow_style=False, allow_unicode=True, Dumper=MyDumper)

    @staticmethod
    def prep_path(path):
        return Path(os.path.join(os.path.dirname(os.path.abspath(__file__)), path)).as_posix() # normalize path

def main():
    config_paths = ConfigPath()

    for path in config_paths.config_paths:
        path["source"] = ConfigPath.prep_path(path["source"])
        path["target"] = ConfigPath.prep_path(path["target"])
        print(path["target"],  path["source"], path["keyword"])
        path_source =path["source"]
        if path["target"].endswith(".py"):
            print("py file")
            ConfigPath.replace_after_keyword_py(path["target"], path["keyword"], f'"{path_source}"')
        else:
            print("yaml file")
            ConfigPath.replace_after_keyword_yaml(path["target"], path["keyword"], path_source)

if __name__ == "__main__":
    main()

# model_llama_dir = os.path.join(base_dir,"checkpoints", "Llama-2-7b-chat-hf")
# target_config_model_path = os.path.join(base_dir,"minigpt4", "configs", "models", "minigpt_v2.yaml")

# model_hubert_dir = os.path.join(base_dir,"checkpoints", "transformer", "chinese-hubert-large")
# target_file_conversation_path = os.path.join(base_dir, "minigpt4", "conversation", "conversation.py")

# model_emotion_llama_path = os.path.join(base_dir,"checkpoints", "save_checkpoint","Emoation_LLaMA.pth")
# target_config_demo_path = os.path.join(base_dir,"eval_configs", "demo.yaml")
