import csv

f = open ('roadcheck2.csv')
csv_f = csv.reader(f)

with open('outRoads.csv', 'wb') as csvfile:
    roadWriter = csv.writer(csvfile, delimiter=',')


    for row in csv_f:
        print row[0]

        endMP = 0
        if row[7] == row[6]: 
            endMP = str(float(row[7]) + 0.01)
        else:
            endMP = row[7]

        if (row[8] == 'E W' or row[8] == 'N S') and (row[5].rstrip().endswith('K') or row[5].rstrip().endswith('H')):
            
            roadWriter.writerow([row[0],row[1],row[2],row[3],row[4],row[5],row[6],endMP,'',row[9],row[10],
                            row[11],row[12],row[13],row[14],row[15],row[16],row[17],row[18],row[19]])
        elif (row[8] == 'E W' or row[8] == 'N S') and ((row[5].rstrip().endswith('K') == False or row[5].rstrip().endswith('H') == False)):
            roadWriter.writerow ([row[0],row[1],row[2],row[3],row[4],row[5],row[6],endMP,row[8][:1],row[9],row[10],
                   str(float(row[11])/2),str(float(row[12])/2),row[13],str(float(row[14])/2),str(float(row[15])/2),
                   str(float(row[16])/2),str(float(row[17])/2),str(float(row[18])/2),str(float(row[19])/2)])
            roadWriter.writerow ([row[0],row[1],row[2],row[3],row[4],row[5],row[6],endMP,row[8][-1],row[9],row[10],
                   str(float(row[11])/2),str(float(row[12])/2),row[13],str(float(row[14])/2),str(float(row[15])/2),
                   str(float(row[16])/2),str(float(row[17])/2),str(float(row[18])/2),str(float(row[19])/2)])
        else:
            roadWriter.writerow ([row[0],row[1],row[2],row[3],row[4],row[5],row[6],endMP,row[8],row[9],row[10],
                            row[11],row[12],row[13],row[14],row[15],row[16],row[17],row[18],row[19]])


    f.close()

    print "Finished Cleanup"

