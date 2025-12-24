from fastmcp import FastMCP
import pandas as pd
import random

# 1. MCP 서버 생성
mcp = FastMCP(
    "DogBreedsWiki",
    instructions="""
    전문적인 반려견 정보 및 생활 환경 매칭 서비스를 제공하는 MCP 서버입니다.
    
    ## 💡 대화 예시 (Prompt Examples)
    1. **"아파트에 혼자 살고 비염이 조금 있어. 털 안 빠지고 짖음 적은 조용한 강아지 추천해 줄 수 있어?"**
       -> `recommend_by_environment` 도구 사용 (생활 환경 매칭)
       
    2. **"포메라니안 성격이랑 활동량이 궁금해. 사진이랑 같이 자세히 보여줘."**
       -> `search_breed_by_name` 도구 사용 (상세 정보 검색)
       
    3. **"요즘 제일 인기 있는 강아지 순위 5위까지만 알려줘."**
       -> `get_top_popularity` 도구 사용 (랭킹 조회)
    """
)

# 2. 데이터 로드 (CSV)
# 전역 변수로 데이터를 로드하여 효율성 증대
try:
    df = pd.read_csv('breeds.csv')
    print(f"Loaded {len(df)} dog breeds.")
except Exception as e:
    print(f"Error loading CSV: {e}")
    df = pd.DataFrame()

@mcp.tool()
def search_breed_by_name(name: str) -> str:
    """
    Search for a dog breed by name (Korean or English) and return its details.
    강아지 견종 이름(한글 또는 영어)으로 정보를 검색합니다.
    """
    if df.empty:
        return "데이터베이스가 비어있습니다."

    name = name.lower().strip()
    
    # 부분 일치 검색
    result = df[
        df['name_ko'].str.contains(name, case=False, na=False) | 
        df['name_en'].str.contains(name, case=False, na=False)
    ]

    if result.empty:
        return f"'{name}'에 대한 검색 결과가 없습니다."
    
    # 검색 결과 중 첫 번째 항목 표시
    breed = result.iloc[0]
    
    # 별 개수 시각화 함수
    def stars(level):
        return '⭐' * int(level) + '☆' * (5 - int(level))

    return f"""
    ### 🐶 {breed['name_ko']} ({breed['name_en']})
    
    ![Image]({breed['thumbnail_url']})
    
    * **크기:** {breed['size_type']}
    * **인기도:** {breed['popularity_score']}점
    
    #### 📊 특성 레벨
    * **⚡ 활동량:** {stars(breed['energy_level'])} ({breed['energy_level']}/5)
    * **🧹 털빠짐:** {stars(breed['shedding_level'])} ({breed['shedding_level']}/5)
    * **📢 짖음:** {stars(breed['barking_level'])} ({breed['barking_level']}/5)
    
    #### 📝 특징
    {breed['summary']}
    
    #### 📜 역사
    {str(breed['history'])[:300]}...
    """

@mcp.tool()
def recommend_by_environment(
    living_space: str = "apartment", 
    activity_level: str = "moderate", 
    concern_shedding: bool = False,
    concern_barking: bool = False
) -> str:
    """
    Recommend dog breeds based on user's living environment and preferences.
    Returns a random selection of suitable breeds to ensure variety.
    
    Args:
        living_space: "apartment" (아파트/빌라) or "house" (마당 있는 주택)
        activity_level: "low" (가벼운 산책), "moderate" (일반), "high" (조깅/등산)
        concern_shedding: True if you want a dog that doesn't shed much (털 빠짐 예민)
        concern_barking: True if you need a quiet dog (짖음 예민)
    """
    if df.empty:
        return "데이터베이스가 비어있습니다."

    candidates = df.copy()

    # 1. 주거 환경 필터링 (아파트면 대형견 제외 권장, 짖음 중요)
    if living_space.lower() in ["apartment", "flat", "아파트", "빌라"]:
        # 아파트에서는 짖음이 매우 심한 개(5점)는 피하는 게 좋음
        candidates = candidates[candidates['barking_level'] <= 4]
        # 초대형견 제외 (선택 사항)
        candidates = candidates[candidates['size_type'] != '대형']

    # 2. 짖음 예민도 (사용자가 명시적으로 조용한 개를 원할 때)
    if concern_barking:
        candidates = candidates[candidates['barking_level'] <= 2]

    # 3. 털 빠짐 필터링
    if concern_shedding:
        candidates = candidates[candidates['shedding_level'] <= 2]

    # 4. 활동량 매칭
    if activity_level.lower() in ["low", "낮음"]:
        candidates = candidates[candidates['energy_level'] <= 2]
    elif activity_level.lower() in ["high", "높음"]:
        candidates = candidates[candidates['energy_level'] >= 4]
    else: # moderate
        candidates = candidates[(candidates['energy_level'] >= 2) & (candidates['energy_level'] <= 4)]

    if candidates.empty:
        return "조건이 너무 까다로워 추천할 강아지가 없습니다. 조건을 조금만 완화해 보세요! (예: 털 빠짐이나 짖음 조건을 하나 끄기)"

    # 5. 다양성 확보 (Random Sampling)
    # 후보군이 많으면 무작위로 3마리 섞어서 추천
    sample_size = min(3, len(candidates))
    recommended = candidates.sample(n=sample_size)
    
    response = f"### 🏠 당신의 환경에 딱 맞는 추천 반려견 ({len(candidates)}마리 중 {sample_size}마리 추천)\n"
    response += "*(질문할 때마다 다른 강아지가 추천될 수 있습니다)*\n\n"
    
    for _, breed in recommended.iterrows():
        response += f"#### 🐾 {breed['name_ko']} ({breed['name_en']})\n"
        response += f"- **크기:** {breed['size_type']} / **활동량:** {int(breed['energy_level'])}/5\n"
        response += f"- **특징:** {breed['summary']}\n"
        response += f"![thumb]({breed['thumbnail_url']})\n\n"
        
    return response

@mcp.tool()
def get_top_popularity(count: int = 5) -> str:
    """
    Get a list of the most popular dog breeds.
    인기 순위 상위 견종을 조회합니다.
    """
    if df.empty: return "데이터베이스가 비어있습니다."

    # 인기 점수 기준 내림차순 정렬 (높을수록 인기 많음)
    top_breeds = df.sort_values(by='popularity_score', ascending=False).head(count)
    
    response = f"### 🏆 인기 강아지 TOP {count}\n\n"
    
    rank = 1
    for _, breed in top_breeds.iterrows():
        response += f"{rank}. **{breed['name_ko']}** ({breed['name_en']}) - {breed['popularity_score']}점\n"
        rank += 1
        
    return response

if __name__ == "__main__":
    mcp.run()