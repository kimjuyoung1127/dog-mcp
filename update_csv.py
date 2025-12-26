import pandas as pd

# 1. Load existing CSV
df = pd.read_csv('breeds.csv')

# 2. Define Trainability Scores (Based on Stanley Coren's Intelligence of Dogs & General Breed Traits)
# 5: 천재형 (가장 훈련하기 쉬움)
# 4: 우등생 (훈련 용이)
# 3: 평균 (반복 훈련 필요)
# 2: 노력형 (독립심 강함, 인내심 필요)
# 1: 자유로운 영혼 (고집 셈, 훈련 어려움)

trainability_map = {
    # 5점: 천재형
    '보더 콜리': 5, '푸들': 5, '저먼 셰퍼드': 5, '골든 리트리버': 5, '도베르만': 5,
    '셔틀랜드 쉽독': 5, '라브라도 리트리버': 5, '파피용': 5, '로트바일러': 5, '오스트레일리안 캐틀독': 5,
    '웰시 코기': 4, '펨브로크 웰시 코기': 4, '미니어처 슈나우저': 4, '잉글리시 스프링거 스패니얼': 4,
    '벨기에 테르뷔렌': 5, '벨기에 말리누아': 5, '보더 테리어': 4, '바이마라너': 5,
    
    # 4점: 우등생 (상위권)
    '포메라니안': 4, '아이리시 세터': 4, '케언 테리어': 4, '요크셔 테리어': 4,
    '자이언트 슈나우저': 4, '에어데일 테리어': 4, '보더 테리어': 4, '비즐라': 4,
    '사모예드': 3, '아메리칸 에스키모견': 4, '비숑 프리제': 4, '아메리칸 워터 스패니얼': 4,
    '코커 스패니얼': 4, '잉글리시 코커 스패니얼': 4, '브리타니': 4,
    
    # 3점: 평균 (보통)
    '몰티즈': 3, '닥스훈트': 3, '미니어처 핀셔': 3, '베들링턴 테리어': 3,
    '그레이하운드': 3, '잭 러셀 테리어': 3, '스태포드셔 불 테리어': 3, '소프트 코티드 휘튼 테리어': 3,
    '카발리에 킹 찰스 스패니얼': 3, '살루키': 3, '포인터': 3, '와이어헤어드 포인팅 그리폰': 3,
    '허스키': 3, '시베리안 허스키': 3, '알래스칸 말라뮤트': 3, '그레이트 데인': 3, '박서': 3,
    '아키타': 3, '시바 이누': 3, '진돗개': 3,
    
    # 2점: 노력형 (하위권 - 독립적)
    '퍼그': 2, '프렌치 불독': 2, '이탈리안 그레이하운드': 2, '일본 친': 2,
    '올드 잉글리시 쉽독': 3, '세인트 버나드': 3, '그레이트 피레네': 3, '치와와': 3,
    '라사압소': 2, '불 테리어': 2, '스코티시 테리어': 2, '스카이 테리어': 2,
    
    # 1점: 자유로운 영혼 (최하위권 - 훈련 매우 어려움)
    '아프간 하운드': 1, '바센지': 1, '불독': 2, '차우차우': 1, '보르조이': 1,
    '블러드하운드': 1, '페키니즈': 1, '비글': 2, '마스티프': 1, '바셋 하운드': 1,
    '시추': 2
}

# English Name fallback mapping (일부 매칭 안될 경우 대비)
trainability_map_en = {
    'Border Collie': 5, 'Poodle': 5, 'German Shepherd Dog': 5, 'Golden Retriever': 5,
    'Doberman Pinscher': 5, 'Shetland Sheepdog': 5, 'Labrador Retriever': 5,
    'Papillon': 5, 'Rottweiler': 5, 'Australian Cattle Dog': 5,
    'Pembroke Welsh Corgi': 4, 'Miniature Schnauzer': 4, 'English Springer Spaniel': 4,
    'Belgian Tervuren': 5, 'Schipperke': 4, 'Keeshond': 4, 'German Shorthaired Pointer': 4,
    'Flat-Coated Retriever': 4, 'English Cocker Spaniel': 4, 'Standard Schnauzer': 4,
    'Brittany': 4, 'Cocker Spaniel': 4, 'Weimaraner': 4, 'Belgian Sheepdog': 4,
    'Bernese Mountain Dog': 4, 'Pomeranian': 4, 'Irish Water Spaniel': 4, 'Vizsla': 4,
    'Cardigan Welsh Corgi': 4, 'Yorkshire Terrier': 3, 'Giant Schnauzer': 4,
    'Airedale Terrier': 4, 'Border Terrier': 4, 'Welsh Springer Spaniel': 4,
    'Manchester Terrier': 3, 'Samoyed': 3, 'Field Spaniel': 3, 'Newfoundland': 4,
    'Australian Terrier': 3, 'Cairn Terrier': 3, 'Gordon Setter': 4,
    'American Staffordshire Terrier': 3, 'Wire Hair Fox Terrier': 3
}

def get_score(row):
    # 1. 한글 이름으로 찾기
    name_ko = row['name_ko'].split('(')[0].strip() # 괄호 제거
    if name_ko in trainability_map:
        return trainability_map[name_ko]
    
    # 2. 영어 이름으로 찾기
    name_en = row['name_en']
    if name_en in trainability_map_en:
        return trainability_map_en[name_en]
    
    # 3. 휴리스틱 (키워드 기반 추정)
    # 셰퍼드, 리트리버, 콜리 계열은 대체로 똑똑함 (4)
    if 'Shepherd' in name_en or 'Retriever' in name_en or 'Collie' in name_en:
        return 4
    if 'Sheepdog' in name_en or 'Cattle' in name_en:
        return 4
        
    # 테리어, 하운드는 대체로 고집이 있음 (3)
    if 'Terrier' in name_en:
        return 3
    if 'Hound' in name_en:
        return 2
        
    # 기본값
    return 3

# 3. Apply Scores
df['trainability'] = df.apply(get_score, axis=1)

# 4. Save
df.to_csv('breeds.csv', index=False)
print(f"Updated breeds.csv with trainability scores. (Default: 3, Total: {len(df)})")
