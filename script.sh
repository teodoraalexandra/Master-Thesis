#!/bin/bash

start=$(date +%s.%N)
# Add permissions: chmod +x script.sh
# Run script: ./script.sh

# Remove the csv files autogenerated from previous run & pictures
rm -f csvs/*
rm -f plots/csvs/*

# Compile the Java program
javac -cp atom-1.14.jar src/Main.java src/NoiseAgent.java src/InformedAgent.java

ROOT_FOLDER=$(dirname "$(realpath "$0")")
export PYTHONPATH=$ROOT_FOLDER

# For loop for our simulations
# Set the number of times to repeat the commands (number of simulations)
n=50
days=40
aggressivity=10
persons=$1
informed=$2 # This is percentage of informed

javaPart() {
  local i=$1

  # Run the program and print the output to prices.csv
  # Require 4 arguments: NUMBER_OF_PERSONS, PERCENTAGE_OF_INFORMED, AGGRESSIVITY, DAYS_OF_SIMULATION
  java -classpath "C:\Users\dant\Desktop\Master-Thesis\src;C:\Users\dant\Desktop\Master-Thesis\atom-1.14.jar" Main "$persons" "$informed" "$aggressivity" "$days" "$i"
  cat "csvs/data$i.csv" | grep "^Price" > "plots/csvs/prices$i$persons$informed.csv"
  cat "csvs/data$i.csv" | grep "^\(Agent\|Day\).*" > "plots/csvs/agents$i.csv"
  sed -i '/noname/d' "plots/csvs/prices$i$persons$informed.csv"
  echo "Java Simulation $i finished." 
}

pythonGraphMetricsPart() {
  total_rows=$(cat plots/csvs/prices1"$persons""$informed".csv | wc -l)
  big_granularity=$((total_rows * 2662 / 1000000))
  small_granularity=$((total_rows * 2662 / 10000000))

  echo "Total rows: $total_rows"
  echo "Big Granularity: $big_granularity"
  echo "Small Granularity: $small_granularity"
  echo "Start Python Computation (Network metrics part)..."

  # Run the Python program for creation
  python "$ROOT_FOLDER"/plots/monte-carlo/graph_metrics.py $n "$persons" "$informed" $big_granularity $small_granularity
  echo -e "Metrics graphs was generated. \n"
}

pythonAgentCashPart() {
  echo "Start Python Computation (Agents' Cash Part)..."

  # Run the Python program for plotting agents' cash
  python "$ROOT_FOLDER"/plots/monte-carlo/agent_cash.py $n "$persons" "$informed" $days
  echo -e "Agents' cash evolution graph was generated. \n"
}

pythonLaplacianMetricsPart() {
  echo "Start Python Computation (Laplacian Metrics Part)..."

  # Run the Python program for computing laplacian metrics
  python "$ROOT_FOLDER"/plots/monte-carlo/laplacian_metrics.py $n "$persons" "$informed"
  echo -e "Laplacian graph was generated. \n"
}

pythonGephiGraphs() {
  echo "Start Python Computation (Graph Gephi)..."

  # Run the Python program for computing graph complex metrics
  python plots/monte-carlo/gephi_graphs.py $n
  echo -e "Graph gephi was generated. \n"
}

echo "Running bash script with $persons agents and $informed percentage"

echo "Start Java Simulation..."
for i in $(seq 1 $n); do
    javaPart "$i" &
done
wait

pythonGraphMetricsPart
#pythonAgentCashPart
#pythonLaplacianMetricsPart

# Use this only for generating gml files
#pythonGephiGraphs

end=$(date +%s.%N)
runtime=$(python -c "print(${end} - ${start})")

echo "Runtime was $runtime seconds."

# For Ubuntu
# java -cp "atom-1.14.jar:." atomSimulation.Main 200 5 10 100
# javac -cp "atom-1.14.jar:." -d . application/src/atomSimulation/Main.java application/src/atomSimulation/InformedAgent.java application/src/atomSimulation/NoiseAgent.java
