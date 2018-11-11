N = ['aaaaaaaaaaaaaaaaaaaaaa']
for b in N:
    # Write Your Code Here
    n=[]
    i=0
    while i < len(b)-2:
        if i!=0:
            if b[i]<=n[-1]:
                i+=1
                continue
            if b[i]>=b[i+1]:           
                if b[i]>b[i+2]:
                    n.append(b[i+1])
                else:
                    n.append(b[i])
                i+=1
            else:
                n.append(b[i])
        else:
            if b[i]>=b[i+1]:           
                if b[i]>b[i+2]:
                    n.append(b[i+1])
                else:
                    n.append(b[i])
                i+=1
            else:
                n.append(b[i])
        i+=1

    if(b[i+1]>b[i]):
        n.append(b[i])
        n.append(b[i+1])