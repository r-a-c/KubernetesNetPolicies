mkdir $1


for i in $(seq 4)
do

/root/apache-jmeter-5.4.1/bin/jmeter -n -t TestPlanBasic.jmx
sleep 15
mv resultados100 $1/resultados100-$i
/root/apache-jmeter-5.4.1/bin/jmeter -g $1/resultados100-$i -o $1/htmlresultados100-$i/


/root/apache-jmeter-5.4.1/bin/jmeter -n -t TestPlanBasic500.jmx
sleep 15
mv resultados500 $1/resultados500-$i
/root/apache-jmeter-5.4.1/bin/jmeter -g $1/resultados500-$i -o $1/htmlresultados500-$i/


/root/apache-jmeter-5.4.1/bin/jmeter -n -t TestPlanBasic1000.jmx
sleep 15
mv resultados1000 $1/resultados1000-$i
/root/apache-jmeter-5.4.1/bin/jmeter -g $1/resultados1000-$i -o $1/htmlresultados1000-$i/

/root/apache-jmeter-5.4.1/bin/jmeter -n -t TestPlanBasic2000.jmx
sleep 15
mv resultados2000 $1/resultados2000-$i
/root/apache-jmeter-5.4.1/bin/jmeter -g $1/resultados2000-$i -o $1/htmlresultados2000-$i/



sleep 20
done


