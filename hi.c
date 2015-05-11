int func(int a)
{
    a = 4;
    return a;
}


int main()
{
    int a,b,c,d,e;
    a = 1;
    b = a;
    c = a +2*b; //can it handle math?
    // d = c; //can it handle comments
    d = a; d = b; //can it hamdle multiple assignments
    e = func(c); //can it handle functions
    
    return 0;
}

