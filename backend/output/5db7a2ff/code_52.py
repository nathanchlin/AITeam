import numpy as np

class MatrixOperations:
    @staticmethod
    def multiply_matrices_batch(matrices_a, matrices_b):
        # 使用NumPy的广播机制批量矩阵乘法
        return np.matmul(matrices_a, matrices_b)