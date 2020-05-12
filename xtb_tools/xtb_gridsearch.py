import os, argparse


def generator(temp, kpush, alpha):
    with open("temp%.2fK_kpush%.2f_alpha%.2f.inp"%(temp, kpush, alpha),'w') as f:
        f.write(

'''$md
   time=10
   step=1
   temp=%.2f
$end
$metadyn
   atoms: 1-3
   save=10
   kpush=%.2f
   alp=%.2f
$end'''%(temp, alpha, kpush))
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    
    parser.add_argument('--temperature',nargs='+', type=float)
    parser.add_argument('--kpush',nargs='+', type=float)
    parser.add_argument('--alpha',nargs='+', type=float)

    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--xtbpath', type=str)
    parser.add_argument('--coord', type=str)


    args = parser.parse_args()

    temps = args.temperature
    kpushs = args.kpush
    alphas = args.alpha

    execute = False
    if args.execute:
        execute = True
        xtbpath = args.xtbpath
        coord = args.coord

    for temp in temps:
        os.mkdir("temp%.2fK"%(temp))
        os.path.chdir("temp%.2fK"%(temp)) 
        for kpush in kpushs:
            os.mkdir("temp%.2fK_kpush%.2f"%(temp, kpush))
            os.path.chdir("temp%.2fK_kpush%.2f"%(temp, kpush))
            for alpha in alphas:
                os.mkdir("temp%.2fK_kpush%.2f_alpha%.2f"%(temp, kpush, alpha))
                os.path.chdir("temp%.2fK_kpush%.2f_alpha%.2f"%(temp, kpush, alpha))

                generator(temp, kpush, alpha)

                if execute:
                    os.system("./%s --md --input temp%.2fK_alpha%.2f_kpush%.2f.inp %s"
                              %(xtbpath, temp, kpush, alpha, coord))
                os.chdir("..")
            os.chdir("..")
        os.chdir("..")
