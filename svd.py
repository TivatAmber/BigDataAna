import numpy as np
import matplotlib.pyplot as plt

# 示例矩阵
# A = np.array([[1, 2], [3, 4], [5, 6]])
A = np.random.random(size=(10, 10))
# A = np.asarray([[1, 1, 1, 0, 0], [3, 3, 3, 0, 0], [4, 4, 4, 0, 0], [5, 5, 5, 0, 0], [0, 2, 0, 4, 4], [0, 0, 0, 5, 5],
#      [0, 1, 0, 2, 2]])

# 进行奇异值分解
U, S, VT = np.linalg.svd(A)

# 构建对角矩阵 Sigma
Sigma = np.zeros_like(A)
Sigma[:np.min(A.shape), :np.min(A.shape)] = np.diag(S)

target = 7
dels = list(range(-target, 0))

U = np.delete(U, dels, axis=1)
Sigma = np.delete(Sigma, dels, axis=1)
Sigma = np.delete(Sigma, dels, axis=0)
VT = np.delete(VT, dels, axis=0)

# 可视化原始矩阵和分解后的矩阵
fig, axs = plt.subplots(1, 5, figsize=(15, 5))

# 原始矩阵 A
axs[0].imshow(A, cmap='viridis', aspect='auto')
axs[0].set_title('Matrix A')
# axs[0].set_xticks(np.arange(A.shape[1]))
# axs[0].set_yticks(np.arange(A.shape[0]))

# 矩阵 U
axs[1].imshow(U, cmap='viridis', aspect='auto')
axs[1].set_title('Matrix U')
# axs[1].set_xticks(np.arange(U.shape[1]))
# axs[1].set_yticks(np.arange(U.shape[0]))

# 矩阵 Sigma
axs[2].imshow(Sigma, cmap='viridis', aspect='auto')
axs[2].set_title('Matrix Σ')
# axs[2].set_xticks(np.arange(Sigma.shape[1]))
# axs[2].set_yticks(np.arange(Sigma.shape[0]))

# 矩阵 V^T
axs[3].imshow(VT, cmap='viridis', aspect='auto')
axs[3].set_title('Matrix V^T')
# axs[3].set_xticks(np.arange(VT.shape[1]))
# axs[3].set_yticks(np.arange(VT.shape[0]))

axs[4].imshow(now_A := np.dot(np.dot(U, Sigma), VT), cmap='viridis', aspect='auto')
axs[4].set_title('Matrix Pro')

print(np.sum((now_A - A) ** 2))
plt.tight_layout()
plt.show()
