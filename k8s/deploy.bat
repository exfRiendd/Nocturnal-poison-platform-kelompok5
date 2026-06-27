kubectl apply -f namespace.yaml
kubectl apply -f secrets.yaml
kubectl apply -f configmap.yaml

kubectl delete configmap mysql-init-sql --namespace=smartcity --ignore-not-found

kubectl create configmap mysql-init-sql --from-file=../database/schema.sql --from-file=../database/seed.sql --namespace=smartcity

kubectl apply -f .
