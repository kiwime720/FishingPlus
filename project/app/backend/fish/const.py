# ─────────────────────────────────────────────────────────────────────────────
#  EcoBank 어류 점 서비스 기본 정보
# ─────────────────────────────────────────────────────────────────────────────

# 베이스 URL
BASE_URL = "https://www.nie-ecobank.kr/ecoapi/NteeInfoService"

# WFS 엔드포인트 경로
WFS_ENDPOINT = "/wfs/getFishesPointWFS"

# ─────────────────────────────────────────────────────────────────────────────
#  요청 파라미터 이름
# ─────────────────────────────────────────────────────────────────────────────
PARAM_SERVICE_KEY  = "serviceKey"
PARAM_TYPE_NAME    = "typeName"    # 피처 타입명(쉼표 구분)
PARAM_BBOX         = "bbox"        # "miny,minx,maxy,maxx"
PARAM_MAX_FEATURES = "maxFeatures" # 최대 피처 개수 (기본 10, 최대 500)

# ─────────────────────────────────────────────────────────────────────────────
#  기본값 (옵션 파라미터 디폴트)
# ─────────────────────────────────────────────────────────────────────────────
DEFAULT_TYPE_NAME    = "mv_map_ecpe_fishes_point"
DEFAULT_MAX_FEATURES = 20
DEFAULT_SRS          = "EPSG:5186"

# ─────────────────────────────────────────────────────────────────────────────
#  WFS 응답 파싱에 사용할 필드명
# ─────────────────────────────────────────────────────────────────────────────
WFS_FIELD_SPC_ID       = "spce_id"
WFS_FIELD_GEOM         = "geom"
WFS_FIELD_EXAMIN_YEAR  = "examin_year"
WFS_FIELD_SPCS_KOR_NAME= "spcs_korean_nm"
WFS_FIELD_AREA_NAME    = "examin_area_nm"
WFS_FIELD_BEGIN_DATE   = "examin_begin_de"
WFS_FIELD_END_DATE     = "examin_end_de"
