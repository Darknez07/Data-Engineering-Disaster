from flask import Flask
from flask import render_template, request, send_file
import pandas as pd
from conv_pdf import PDF
df = pd.read_csv("..\Hazard_Ranked.csv")
ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4])
app = Flask(__name__)

@app.route('/',methods=['GET','POST'])
def router():
    if request.method == 'GET':
        return render_template('index.html', answer=False)
    else:
        try:
            val = int(request.form['dis'])
        except:
            val = 0
        print(val)
        return render_template('index.html', answer=True,num=val)

@app.route('/submit',methods=['POST','GET'])
def subs():
    del df[df.columns[0]]
    if request.method == 'POST':
        rankings = []
        paths = "Files/"
        number = 1
        basic = "Files/Template_diss.txt"
        modif = open(basic,'r').read().split(' ')
        modif.append('\n')
        modif.append('\n')
        text_fill = {}
        pdf = PDF()
        pdf.set_title('Lol')
        pdf.set_author('Rishi Kakkar, Akshat Singh, Rahul Pandey, Subham Shah, Nitesh Jha')
        for ans in request.json:
            print(ans)
            filler = []
            filler.append("Disaster_"+str(number))

            l = list(map(int, list(ans.values())))
            print(l)
            impact = l[1]*2+l[2]*1+l[3]*3
            txt = ("1. "+open(paths+"Population_"+str(l[3])+".txt",'r').read()+"\n\n")
            txt+=("2. "+open(paths+"Economic_"+str(l[1])+".txt",'r').read()+"\n\n")
            txt+=("3. "+open(paths+"Property_"+str(l[2])+".txt",'r').read()+'\n')
            text_fill[filler[0]] = txt
            Ranking = l[0]*impact

            # Code to choose the nearest values to ranking

            nearest_ranking = df.iloc[(df["Hazard_ranking"] - Ranking).abs().argsort()[:2]]
            ans = nearest_ranking[nearest_ranking['Rating'] == l[0]]
            disas = None

            if ans.shape[0] == 0:
                find_from = df[df['Rating'] == l[0]]
                nearest_ranking = find_from.iloc[(find_from["Hazard_ranking"] - Ranking).abs().argsort()]
                ans = nearest_ranking.sort_values(by=['Population_impact','Economic_impact','Property_impact'],ascending=False)
                disas = ans['incident_type'].values[0]
            else:
                ans = ans.sort_values(by=['Population_impact','Economic_impact','Property_impact'],ascending=False)
                disas = ans['incident_type'].values[0]
            if disas is not None:
                filler.append(disas)
            cond = ((df["Hazard_ranking"] - Ranking).abs().sort_values() == 0.0)
            if df[cond].shape[0] > 0:
                filler.append(100)
            else:
                filler.append(((2*Ranking - ans['Hazard_ranking']).abs()/Ranking).values[0]*100)
            filler+=[l[3],l[1],l[2]]
            print(filler)
            rankings.append([Ranking,filler])
            number+=1
        rankings = sorted(rankings,key=lambda x: (x[0],x[1][3],x[1][4],x[1][5]),reverse=True)
        num = 1
        for rank in rankings:
            rank[1].insert(3,ordinal(num))
            num+=1
        pages = []
        chp = 1
        for rank in rankings:
            num = 0
            page = ""
            done = False
            print(rank)
            for w in modif:
                if w.find(';') != -1:
                    if not done and num == 4:
                        w = w.replace(';',str(rank[0]))
                        done = True
                    else:
                        w = w.replace(';',str(rank[1][num]))
                        num+=1
                page = page+" "+w
            page+=text_fill[rank[1][0]]
            pdf.print_chapter(chp,'Assessment for '+rank[1][0], page)
            chp+=1
        pdf.output('Document.pdf','F')
    return send_file('Document.pdf',as_attachment=True)

if __name__ == '__main__':
    app.run('0.0.0.0',debug=True)