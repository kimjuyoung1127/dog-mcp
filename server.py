# -*- coding: utf-8 -*-
from fastmcp import FastMCP
import pandas as pd
import random
from difflib import get_close_matches

# 1. MCP 서버 생성
mcp = FastMCP(
    "DogBreedsWiki",
    instructions="""
    전문적인 반려견 정보 및 생활 환경 매칭 서비스를 제공하는 MCP 서버입니다.
    
    ## [활용 팁]
    1. **맞춤 추천:** "아파트 거주, 털 빠짐 예민, 활동량 보통, 초보자입니다" 처럼 구체적인 환경을 말하면 적합도 점수가 높은 견종을 추천합니다.
    2. **비교 분석:** 두 견종 중 고민된다면 "말티즈랑 푸들 비교해줘"라고 요청하세요.
    3. **스마트 검색:** 별명(인절미, 소시지독)으로 검색하거나 오타가 있어도 올바른 견종을 찾아줍니다.
    ""
)

# 별칭 사전
NICKNAMES = {
    "인절미": "골든 리트리버",
    "소시지독": "닥스훈트",
    "사자개": "차우차우",
    "천사견": "골든 리트리버",
    "악마견": "비글",
    "지랄견": "비글",
    "백구": "진돗개"
}

# 2. 데이터 로드
try:
    df = pd.read_csv('breeds.csv')
    print(f"Loaded {len(df)} dog breeds.")
except Exception as e:
    print(f"Error loading CSV: {e}")
    df = pd.DataFrame()

def get_stars(level):
    try:
        level = int(float(level))
        return '★' * level + '☆' * (5 - level)
    except:
        return 'N/A'

@mcp.tool()
def search_breed_by_name(name: str) -> str:
    """
    강아지 견종 이름(한글/영어) 또는 별명으로 정보를 검색합니다.
    오타가 있는 경우 비슷한 이름을 추천합니다.
    """
    if df.empty: return "데이터베이스가 비어있습니다."

    query = name.lower().strip()
    
    # 1. 별칭 확인
    if query in NICKNAMES:
        query = NICKNAMES[query]

    # 2. 정확도/부분 일치 검색
    result = df[
        df['name_ko'].str.contains(query, case=False, na=False) | 
        df['name_en'].str.contains(query, case=False, na=False)
    ]

    if result.empty:
        # 3. 오타 보정 (유사도 검색)
        all_names = df['name_ko'].tolist() + df['name_en'].tolist()
        similar = get_close_matches(query, all_names, n=1, cutoff=0.5)
        if similar:
            return f"'{name}'에 대한 검색 결과가 없습니다. 혹시 **'{similar[0]}'**를 찾으시는 건가요?"
        return f"'{name}'에 대한 검색 결과가 없습니다."
    
    breed = result.iloc[0]
    
    # 지능/훈련 난이도 멘트
    train_score = breed.get('trainability', 3)
    train_desc = "천재형 (훈련이 매우 쉬움)" if train_score == 5 else \
                 "우등생 (잘 배움)" if train_score == 4 else \
                 "보통 (반복 학습 필요)" if train_score == 3 else \
                 "노력형 (인내심 필요)" if train_score == 2 else "자유로운 영혼 (훈련 어려움)"

    return f"""
### [견종 정보] {breed['name_ko']} ({breed['name_en']})

![Image]({breed['thumbnail_url']})

* **크기:** {breed['size_type']}
* **수명:** {breed['avg_life_expectancy']}년 / **체중:** {breed['avg_weight']}kg
* **인기도:** {breed['popularity_score']}점

#### [특성 지표]
* **[지능/훈련]:** {get_stars(train_score)} ({train_desc})
* **[활동량]:** {get_stars(breed['energy_level'])} ({breed['energy_level']}/5)
* **[털빠짐]:** {get_stars(breed['shedding_level'])} ({breed['shedding_level']}/5)
* **[짖음]:** {get_stars(breed['barking_level'])} ({breed['barking_level']}/5)

#### [요약]
{breed['summary']}

#### [유래]
{str(breed['history'])[:300]}...
"""

@mcp.tool()
def recommend_by_environment(
    living_space: str = "apartment", 
    activity_level: str = "moderate", 
    concern_shedding: bool = False,
    concern_barking: bool = False,
    is_beginner: bool = False
) -> str:
    """
    사용자의 환경에 가장 잘 맞는 반려견을 점수 기반(Match Score)으로 추천합니다.
    """
    if df.empty: return "데이터베이스가 비어있습니다."

    temp_df = df.copy()
    temp_df['match_score'] = 100

    # 목표 활동량 수치화
    target_energy = 2 if activity_level == "low" else (5 if activity_level == "high" else 3)

    for idx, row in temp_df.iterrows():
        score = 100
        if living_space in ["apartment", "아파트", "빌라"]:
            if row['barking_level'] >= 4: score -= 30
            if row['size_type'] == '대형': score -= 25
        if concern_barking:
            score -= (row['barking_level'] * 10)
        if concern_shedding:
            score -= (row['shedding_level'] * 10)
        energy_diff = abs(row['energy_level'] - target_energy)
        score -= (energy_diff * 15)
        if is_beginner:
            train_score = row.get('trainability', 3)
            if train_score >= 4: score += 10
            elif train_score <= 2: score -= 20
        temp_df.at[idx, 'match_score'] = score

    top_3 = temp_df.sort_values(by='match_score', ascending=False).head(3)
    
    response = f"### [추천 결과] 당신을 위한 맞춤 반려견 TOP 3\n"
    beginner_str = "O" if is_beginner else "X"
    response += f"*환경: {living_space} / 활동: {activity_level} / 초보자: {beginner_str}*\n\n"
    
    for _, breed in top_3.iterrows():
        match_pct = max(0, min(100, breed['match_score']))
        train_val = breed.get('trainability', 3)
        
        response += f"#### - {breed['name_ko']} (적합도: {int(match_pct)}점)\n"
        response += f"- **훈련 난이도:** {get_stars(train_val)}\n"
        response += f"- **특징:** {breed['summary']}\n"
        
        reason = ""
        if breed['barking_level'] <= 2 and living_space == 'apartment':
            reason += "아파트 생활에 적합하고 "
        
        if is_beginner and train_val >= 4:
            reason += "지능이 높아 초보자도 훈련하기 쉽습니다.\n"
        else:
            reason += "털 관리가 편합니다.\n" if breed['shedding_level'] <= 2 else "활동 성향이 잘 맞습니다.\n"
            
        response += f"- **추천 이유:** {reason}"
        response += f"![thumb]({breed['thumbnail_url']})\n\n"
        
    return response

@mcp.tool()
def compare_breeds(breed1_name: str, breed2_name: str) -> str:
    """
    두 견종의 주요 특징과 스펙을 표 형태로 상세하게 비교합니다.
    """
    def find_breed(name):
        name = name.lower().strip()
        if name in NICKNAMES: name = NICKNAMES[name]
        res = df[df['name_ko'].str.contains(name, na=False) | df['name_en'].str.contains(name, case=False, na=False)]
        return res.iloc[0] if not res.empty else None

    b1 = find_breed(breed1_name)
    b2 = find_breed(breed2_name)

    if b1 is None or b2 is None:
        return "비교할 견종을 찾을 수 없습니다."

    better_train = b1['name_ko'] if b1.get('trainability', 3) >= b2.get('trainability', 3) else b2['name_ko']
    better_shed = b1['name_ko'] if b1['shedding_level'] <= b2['shedding_level'] else b2['name_ko']

    return f"""
### [비교 분석]: {b1['name_ko']} vs {b2['name_ko']}

| 특징 | {b1['name_ko']} | {b2['name_ko']} |
| :--- | :---: | :---: |
| **크기** | {b1['size_type']} | {b2['size_type']} |
| **지능(훈련)** | {get_stars(b1.get('trainability', 3))} | {get_stars(b2.get('trainability', 3))} |
| **활동량** | {get_stars(b1['energy_level'])} | {get_stars(b2['energy_level'])} |
| **털빠짐** | {get_stars(b1['shedding_level'])} | {get_stars(b2['shedding_level'])} |
| **짖음** | {get_stars(b1['barking_level'])} | {get_stars(b2['barking_level'])} |

**[참고 팁]:**
- 훈련이 더 쉬운 개는 **{better_train}**입니다.
- 털 관리가 더 편한 개는 **{better_shed}**입니다.
"""

@mcp.tool()
def get_top_popularity(count: int = 5) -> str:
    """인기 순위 상위 견종을 조회합니다."""
    if df.empty: return "데이터 없음"
    top_breeds = df.sort_values(by='popularity_score', ascending=False).head(count)
    response = f"### [인기 순위] 인기 강아지 TOP {count}\n\n"
    for i, (_, breed) in enumerate(top_breeds.iterrows(), 1):
        response += f"{i}. **{breed['name_ko']}** - {breed['popularity_score']}점\n"
    return response

if __name__ == "__main__":
    mcp.run()
