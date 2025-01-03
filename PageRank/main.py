import numpy as np

relative_path = '../MapReduce/sorted_relative_result.txt'
mapping_path = 'mapping.txt'
ans_path = 'ans.txt'
beta = 0.85
epsilon = 1e-8


def has_circle(dfs_graph: np.ndarray):
    visit = np.zeros(dfs_graph.shape[0])

    def dfs(now_node: int, stack: list[int]) -> bool:
        visit[now_node] = 1
        ret_val = False
        stack.append(now_node)

        for target in range(dfs_graph.shape[1]):
            if dfs_graph[now_node][target] and visit[target] == 0:
                ret_val |= dfs(target, stack)
            elif stack.count(target):
                return True

        stack.remove(stack[-1])
        return ret_val

    ret = False
    for now in range(dfs_graph.shape[0]):
        if visit[now] == 0:
            ret |= dfs(now, [])
    return ret


def has_dead_end(now_graph: np.ndarray) -> bool:
    dead_ends = []
    for index, row in enumerate(now_graph):
        if np.sum(row) == 0:
            dead_ends.append(index)
    return len(dead_ends) > 0


if __name__ == '__main__':
    with open(relative_path, 'r') as fp:
        relative = eval(fp.read())
    relative: dict[str, set[str]]
    str_to_int: dict[str, int] = {}

    for key, value in relative.items():
        if str_to_int.get(key) is None:
            str_to_int[key] = len(str_to_int)
        for word in value:
            if str_to_int.get(word) is None:
                str_to_int[word] = len(str_to_int)

    with open(mapping_path, 'w') as fp:
        for key, value in str_to_int.items():
            fp.write(f"{key}, {value}\n")

    graph = np.ndarray(shape=(len(str_to_int), len(str_to_int)))

    val = np.asarray([1 / len(str_to_int)] * len(str_to_int))
    # val = np.asarray([1] * len(str_to_int))
    val = val.reshape(-1, 1)
    val = val.T
    bias = np.asarray([1 / len(str_to_int)] * len(str_to_int))
    bias = bias.reshape(-1, 1)
    bias = bias.T
    print(val.shape)

    for key, value in relative.items():
        for word in value:
            graph[str_to_int[key], str_to_int[word]] = 1

    print(f"Has Circle: {has_circle(graph)}")
    print(f"Has Dead end: {has_dead_end(graph)}")

    basic_matrix = np.ndarray(shape=graph.shape)
    for row_index in range(basic_matrix.shape[0]):
        row_sum = np.sum(graph[row_index])
        if row_sum == 0: continue
        now_val = 1 / row_sum
        for col_index in range(basic_matrix.shape[1]):
            if graph[row_index][col_index] == 1:
                basic_matrix[row_index][col_index] = now_val

    lst_val = np.zeros_like(val)
    iteration_time = 0
    while np.any(np.abs(lst_val - val) > epsilon):
        lst_val = val
        val = beta * val @ basic_matrix + (1 - beta) * bias
        iteration_time += 1
    print(iteration_time)
    # for epoch in range(100000):
    #     val = beta * val @ basic_matrix + (1 - beta) * bias

    val = val.T.squeeze()
    ans: dict[str, int] = {}
    for key, value in str_to_int.items():
        ans[key] = val[value]

    ans: list[tuple[str, int]] = sorted(list(ans.items()), key=lambda x: x[1], reverse=True)
    with open(ans_path, 'w') as fp:
        for key, value in ans:
            fp.write(f"node : {key} - value: {value}\n")
            # fp.write(f"node: {key} - value: {value:.5f}\n")
