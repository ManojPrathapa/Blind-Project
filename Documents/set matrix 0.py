def setmatrix(matrix):
    row=len(matrix)
    col=len(matrix[0])
    zero_row=set()
    zero_col=set()
    for i in range(row):
        for j in range(col):
            if matrix[i][j]==0:
                zero_row.add(i)
                zero_col.add(j)
    for i in range(row):
        for j in range(col):
            if i in zero_row or j in zero_col:
                matrix[i][j]=0 