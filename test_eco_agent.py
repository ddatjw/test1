import os
import json
from pathlib import Path
from PIL import Image
import google.generativeai as genai

# .env 파일에서 API 키 로드 (또는 환경변수 직접 설정)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class EcoVisionAgent:
    def __init__(self):
        """Vision Agent 초기화 및 Gemini 모델 설정"""
        self.api_key = os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY 환경 변수가 설정되지 않았습니다.")
        
        genai.configure(api_key=self.api_key)
        # 이미지 인식과 텍스트 생성이 모두 뛰어난 모델 사용
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        print("[AGENT] Vision Agent가 성공적으로 초기화되었습니다.")

    def analyze_image(self, image_path: str) -> dict:
        """
        이미지 파일을 읽어 분리수거 정보를 분석합니다.
        """
        try:
            # 1. 이미지 파일 로드
            if not os.path.exists(image_path):
                return {"error": f"파일을 찾을 수 없습니다: {image_path}"}
                
            img = Image.open(image_path)
            print(f"[AGENT] 이미지 로드 완료: {image_path}")

            # 2. AI에게 내릴 프롬프트 작성 (지역 맞춤형 지시)
            prompt = """
            당신은 환경 보호 전문가이자 쓰레기 분리배출 안내 에이전트입니다.
            제공된 사진 속 물건을 분석하고, 다음 형식의 JSON으로만 응답해주세요.
            군포시의 최신 쓰레기 분리배출 안내 가이드를 기준으로 정확하게 설명해주세요.

            응답 형식:
            {
                "object_name": "물건의 일반적인 이름",
                "components": [
                    {"part": "뚜껑", "material": "플라스틱"},
                    {"part": "본체", "material": "투명페트"},
                    {"part": "라벨", "material": "비닐"}
                ],
                "disposal_steps": [
                    "1. 내용물을 비우고 물로 헹굽니다.",
                    "2. 라벨을 떼어내어 비닐류로 배출합니다.",
                    "3. 뚜껑을 닫아(또는 분리하여) 투명페트병 전용 수거함에 버립니다."
                ],
                "warning": "주의사항 (예: 이물질이 지워지지 않으면 종량제 봉투에 버리세요)"
            }
            """

            # 3. 모델에 이미지와 프롬프트 전송
            print("[AGENT] AI가 이미지를 분석 중입니다. 잠시만 기다려주세요...")
            response = self.model.generate_content([prompt, img])
            
            # 4. 응답 결과에서 JSON 텍스트 파싱
            response_text = response.text.strip()
            
            # 마크다운 코드 블록 제거
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0].strip()
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0].strip()
                
            return json.loads(response_text)

        except json.JSONDecodeError:
            print("[ERROR] AI의 응답을 JSON으로 변환할 수 없습니다.")
            print(f"원시 응답: {response.text}")
            return {"error": "JSON 파싱 실패"}
        except Exception as e:
            print(f"[ERROR] 분석 중 예기치 않은 오류 발생: {e}")
            return {"error": str(e)}

def main():
    print("=" * 50)
    print("♻️  Eco Agent CLI 테스트 환경 ♻️")
    print("=" * 50)

    try:
        # 에이전트 생성
        agent = EcoVisionAgent()
    except Exception as e:
        print(f"초기화 오류: {e}")
        return

    # 사용자 입력 루프
    while True:
        print("\n" + "-" * 50)
        image_path = input("분석할 쓰레기 이미지의 파일 경로를 입력하세요 (종료하려면 'q' 입력): ").strip()
        
        if image_path.lower() == 'q':
            print("프로그램을 종료합니다.")
            break
            
        if not image_path:
            continue

        # 분석 실행
        result = agent.analyze_image(image_path)
        
        # 결과 출력
        print("\n" + "=" * 50)
        print("📊 분석 결과")
        print("=" * 50)
        print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()