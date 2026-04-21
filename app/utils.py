# # import matplotlib.pyplot as plt
# # import os
# # import pandas as pd
# #
# #
# # def generate_scatter_plot(user_data, cluster_id):
# #     """
# #     user_data: 현재 사용자의 [x, y] 좌표 (PCA 변환된 값)
# #     cluster_id: 현재 사용자의 군집 번호
# #     """
# #     # 1. 가상의 전체 데이터 생성 (실제로는 DB나 CSV에서 불러온 전체 데이터를 사용하세요)
# #     # 여기서는 시연을 위해 랜덤 데이터를 생성합니다.
# #     import numpy as np
# #     # 100개 -> 3000개로 변경 (빽빽함을 결정하는 부분)
# #     mock_data = np.random.randn(3000, 2)
# #     mock_clusters = np.random.randint(0, 3, 3000)
# #
# #     plt.figure(figsize=(8, 6))
# #
# #     # 2. 전체 데이터 산점도 (배경)
# #     colors = ['#FFD8A8', '#A2E0F9', '#D1FFD1']  # 각 군집별 연한 색상
# #     # for i in range(3):
# #     #     points = mock_data[mock_clusters == i]
# #     #     plt.scatter(points[:, 0], points[:, 1], c=colors[i], s=10, alpha=0.3, label=f'Group {i}')
# #
# #     for i in range(3):
# #         points = mock_data[mock_clusters == i]
# #         # marker='o' 를 추가하여 배경은 원형 점으로 그립니다.
# #         plt.scatter(points[:, 0], points[:, 1], c=colors[i], s=10, alpha=0.3,
# #                     marker='o', edgecolors='none', label=f'Group {i}')  # s와 alpha 조절로 빽빽함 유지
# #
# #     # 3. 현재 사용자 위치 강조 (별 모양 또는 큰 점)
# #     user_colors = ['#FF922B', '#339AF0', '#51CF66']  # 강조용 진한 색상
# #     # plt.scatter(user_data, user_data, c='red', s=150, #c=user_colors[cluster_id],
# #     #             edgecolors='black', linewidth=2, marker='*', label='You')
# #
# #     plt.scatter(*user_data, c=user_colors[cluster_id],
# #                 s=200, edgecolors='black', linewidth=2, marker='*', label='You')
# #
# #
# #     # 4. 디자인 정리 (축 제거 및 스타일)
# #     plt.title('Your Health Position in Groups', fontsize=15, pad=20)
# #     plt.legend()
# #     plt.grid(True, linestyle='--', alpha=0.3)
# #
# #     # 축 범위를 스케일링된 표준 범위(-4 ~ 4 정도)로 고정하면
# #     # 사용자가 이상치(Outlier)일지라도 군집이 잘 보입니다.
# #     plt.xlim(-4, 4)
# #     plt.ylim(-4, 4)
# #
# #     # 배경 점들이 너무 퍼져 보인다면 랜덤 생성이 아니라
# #     # 실제 학습 데이터의 일부를 가져와서 그리는 것이 정확합니다.
# #
# #     # 5. 이미지 저장 경로 설정
# #     static_path = os.path.join('app', 'static', 'images', 'scatter_plot.png')
# #
# #     # 폴더가 없으면 생성
# #     os.makedirs(os.path.dirname(static_path), exist_ok=True)
# #
# #     # 저장 후 닫기 (메모리 관리)
# #     plt.savefig(static_path, bbox_inches='tight')
# #     plt.close()
#
#
# import matplotlib.pyplot as plt
# import os
# import pandas as pd
# import numpy as np
#
#
# def generate_scatter_plot(user_data, cluster_id):
#     """
#     user_data: [x, y] 형태의 리스트 (이미 PCA 변환된 값)
#     cluster_id: 현재 사용자의 군집 번호 (0, 1, 2...)
#     """
#     # 1. 실제 PCA 변환된 배경 데이터 로드
#     csv_path = os.path.join('data', 'pca_transformed_data.csv')
#
#     if os.path.exists(csv_path):
#         bg_df = pd.read_csv(csv_path)
#     else:
#         # 파일이 없을 경우를 대비한 방어 코드 (작동은 해야 하므로)
#         print("⚠️ 배경 데이터 파일을 찾을 수 없어 임시 데이터를 사용합니다.")
#         bg_df = pd.DataFrame(np.random.randn(3000, 2), columns=['PC1', 'PC2'])
#         bg_df['Cluster'] = np.random.randint(0, 3, 3000)
#
#     plt.figure(figsize=(10, 7))
#
#     # 2. 배경 데이터 산점도 (실제 모델링 데이터 분포)
#     # 이미지와 비슷한 파스텔톤/비비드톤 색상 설정
#     bg_colors = ['#FFD8A8', '#A2E0F9', '#D1FFD1', '#E5DBFF']
#
#     for i in sorted(bg_df['Cluster'].unique()):
#         points = bg_df[bg_df['Cluster'] == i]
#         plt.scatter(
#             points['PC1'], points['PC2'],
#             c=bg_colors[int(i) % len(bg_colors)],
#             s=15, alpha=0.3, marker='o', edgecolors='none',
#             label=f'Group {i}'
#         )
#
#     # 3. 현재 사용자 위치 강조 (별 모양)
#     # 강조용 진한 색상
#     user_colors = ['#FF922B', '#339AF0', '#51CF66', '#845EF7']
#
#     # *user_data를 사용해 [x, y]를 각각 매개변수로 전달 (별 하나만 찍힘)
#     plt.scatter(
#         *user_data,
#         c=user_colors[cluster_id % len(user_colors)],
#         s=350, edgecolors='black', linewidth=2,
#         marker='*', label='You', zorder=5  # zorder를 높여 별이 가장 위에 오도록 함
#     )
#
#     # 4. 디자인 및 스타일 정리
#     plt.title('Health Data Clusters (PCA 2D Visualization)', fontsize=16, pad=20)
#     plt.xlabel('Principal Component 1', fontsize=12)
#     plt.ylabel('Principal Component 2', fontsize=12)
#
#     # 축 범위 설정 (데이터의 최소/최대값에 맞춰 여백을 줌)
#     # margin = 1.5
#     # plt.xlim(bg_df['PC1'].min() - margin, bg_df['PC1'].max() + margin)
#     # plt.ylim(bg_df['PC2'].min() - margin, bg_df['PC2'].max() + margin)
#
#     x, y = user_data
#     zoom = 1.5
#
#     plt.xlim(min(x - zoom, bg_df['PC1'].min()), max(x + zoom, bg_df['PC1'].max()))
#     plt.ylim(min(y - zoom, bg_df['PC2'].min()), max(y + zoom, bg_df['PC2'].max()))
#
#
#
#
#     plt.legend(loc='upper right')
#     plt.grid(True, linestyle='--', alpha=0.4)
#
#     # 5. 이미지 저장
#     static_path = os.path.join('app', 'static', 'images', 'scatter_plot.png')
#     os.makedirs(os.path.dirname(static_path), exist_ok=True)
#
#     plt.savefig(static_path, bbox_inches='tight', dpi=150)  # 해상도를 높여 선명하게 저장
#     plt.close()

import matplotlib

# [수정 1] 백엔드를 'Agg'로 설정 (GUI 없이 파일 저장만 수행)
# 반드시 pyplot을 import하기 전에 실행되어야 합니다.
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import os
import pandas as pd
import numpy as np


def generate_scatter_plot(user_data, cluster_id):
    """
    user_data: [x, y] 형태의 리스트 (이미 PCA 변환된 값)
    cluster_id: 현재 사용자의 군집 번호 (0, 1, 2...)
    """
    # 1. 실제 PCA 변환된 배경 데이터 로드
    # (경로 설정 시 app 폴더 내부인지 외부인지 확인 필요 - 현재 구조에 맞춰 조정)
    csv_path = os.path.join('data', 'pca_transformed_data.csv')

    if os.path.exists(csv_path):
        bg_df = pd.read_csv(csv_path)
    else:
        print("⚠️ 배경 데이터 파일을 찾을 수 없어 임시 데이터를 사용합니다.")
        bg_df = pd.DataFrame(np.random.randn(3000, 2), columns=['PC1', 'PC2'])
        bg_df['Cluster'] = np.random.randint(0, 3, 3000)

    # [수정 2] 새로운 그래프를 그리기 전에 이전 그림을 완전히 비움 (메모리 관리)
    plt.clf()
    plt.figure(figsize=(10, 7))

    # 2. 배경 데이터 산점도
    bg_colors = ['#FFD8A8', '#A2E0F9', '#D1FFD1', '#E5DBFF']
    for i in sorted(bg_df['Cluster'].unique()):
        points = bg_df[bg_df['Cluster'] == i]
        plt.scatter(
            points['PC1'], points['PC2'],
            c=bg_colors[int(i) % len(bg_colors)],
            s=15, alpha=0.3, marker='o', edgecolors='none',
            label=f'Group {i}'
        )

    # 3. 현재 사용자 위치 강조 (별 모양)
    user_colors = ['#FF922B', '#339AF0', '#51CF66', '#845EF7']
    plt.scatter(
        user_data, user_data,  # 명시적으로 x, y 전달
        c=user_colors[cluster_id % len(user_colors)],
        s=350, edgecolors='black', linewidth=2,
        marker='*', label='You', zorder=5
    )

    # 4. 디자인 및 스타일 정리
    plt.title('Health Data Clusters (PCA 2D Visualization)', fontsize=16, pad=20)
    plt.xlabel('Principal Component 1', fontsize=12)
    plt.ylabel('Principal Component 2', fontsize=12)

    x, y = user_data
    zoom = 1.5
    plt.xlim(min(x - zoom, bg_df['PC1'].min()), max(x + zoom, bg_df['PC1'].max()))
    plt.ylim(min(y - zoom, bg_df['PC2'].min()), max(y + zoom, bg_df['PC2'].max()))

    plt.legend(loc='upper right')
    plt.grid(True, linestyle='--', alpha=0.4)

    # 5. 이미지 저장
    # 경로가 'app/static/images/scatter_plot.png' 인지 확인 (Flask 구조에 따라 'static/images/...' 일 수 있음)
    static_path = os.path.join('app', 'static', 'images', 'scatter_plot.png')
    os.makedirs(os.path.dirname(static_path), exist_ok=True)

    plt.savefig(static_path, bbox_inches='tight', dpi=150)

    # [수정 3] 사용이 끝난 플롯을 메모리에서 완전히 해제 (에러 방지의 핵심)
    plt.close('all')