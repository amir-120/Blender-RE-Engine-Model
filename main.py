import timeit

def first():
    lis = [1, 1,  1, 2, 2, 5, 5, 6, 6]
    list(dict.fromkeys(lis))

def second():
    lis = [1, 1, 1, 2, 2, 5, 5, 6, 6]
    list(set(lis))


if __name__ == '__main__':
    #nicoPath = r"C:\Users\Darkness\Desktop\Mod Tools FQ\re_chunk_000\natives\x64\character\p" \
    #    r"layer\pl0400_nico\pl0400_11_head_event\pl0400_11.mesh.1808282334"
#
    #vergilPath = r"C:\Users\Darkness\Desktop\Mod Tools FQ\re_chunk_000\natives\x64\character\player\pl0300_vergil\p" \
    #    r"l0300_body\pl0300.mesh.1808282334"
#
    #nico = ReadREModel(nicoPath)
    #u = nico.mainModel.lodGroups[0].mainmeshes[2].submeshes[0].uv0s
    #print(u[-1].u, u[-1].v)
    first = timeit.timeit(first, number=1000000)
    print(first)

    second = timeit.timeit(second, number=1000000)
    print(second)
