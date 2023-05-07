#!/bin/bash

start=$(date +%s.%N)
# Add permissions: chmod +x script.sh
# Run script: ./script.sh

# Remove the csv files autogenerated from previous run & pictures
rm -f "price_evolution.png"
rm -f "random_chosen_network.png"
rm -f "plot_PIN_assortativity.png"
rm -f "plot_PIN_density.png"
rm -f "plot_PIN_bipartivity.png"
rm -f "plot_PIN_average_clustering.png"
rm -f "plot_PIN_connected_components.png"
rm -f "plot_PIN_stars.png"
rm -f "agents_cash_evolution.png"
rm -f "laplacian.png"
rm -f "plot_PIN_core.png"
rm -f "plot_PIN_diameter.png"
rm -f "plot_PIN_eccentricity.png"
rm -f "plot_PIN_independence.png"
rm -f "plot_PIN_radius.png"
rm -f csvs/*
rm -f plots/csvs/*

# Compile the Java program
javac -cp atom-1.14.jar src/Main.java src/NoiseAgent.java src/InformedAgent.java

# For loop for our simulations
# Set the number of times to repeat the commands (number of simulations)
n=5
days=100
aggressivity=10
persons=1000
informed=0.5 # This is percentage of informed

javaPart() {
  local i=$1

  # Run the program and print the output to prices.csv
  # Require 4 arguments: NUMBER_OF_PERSONS, PERCENTAGE_OF_INFORMED, AGGRESSIVITY, DAYS_OF_SIMULATION
  java -classpath "C:\Users\dant\Desktop\Master-Thesis\src;C:\Users\dant\Desktop\Master-Thesis\atom-1.14.jar" Main "$persons" "$informed" "$aggressivity" "$days" "$i"
  cat "csvs/data$i.csv" | grep "^Price" > "plots/csvs/prices$i.csv"
  cat "csvs/data$i.csv" | grep "^\(Agent\|Day\).*" > "plots/csvs/agents$i.csv"
  sed -i '/noname/d' "plots/csvs/prices$i.csv"
}

pythonGraphMetricsPart() {
  echo "Start Python Computation (Network metrics part)..."

  # Run the Python program for creation
  python plots/monte-carlo/graph_metrics.py $n $days
  echo -e "Metrics graphs was generated. \n"
}

pythonAgentCashPart() {
  echo "Start Python Computation (Agents' Cash Part)..."

  # Run the Python program for plotting agents' cash
  python plots/monte-carlo/agent_cash.py $n $days
  echo -e "Agents' cash evolution graph was generated. \n"
}

pythonLaplacianMetricsPart() {
  echo "Start Python Computation (Laplacian Metrics Part)..."

  # Run the Python program for computing laplacian metrics
  python plots/monte-carlo/laplacian_metrics.py $n
  echo -e "Laplacian graph was generated. \n"
}

pythonGraphComplexMetricsPart() {
  echo "Start Python Computation (Graph Complex Metrics Part)..."

  # Run the Python program for computing graph complex metrics
  python plots/monte-carlo/graph_complex_metrics.py $n
  echo -e "Graph complex metrics was generated. \n"
}

echo "Start Java Simulation..."
for i in $(seq 1 $n); do
    javaPart "$i" &
done
wait

#pythonGraphMetricsPart
#pythonAgentCashPart
pythonLaplacianMetricsPart
#pythonGraphComplexMetricsPart

end=$(date +%s.%N)
runtime=$(python -c "print(${end} - ${start})")

echo "Runtime was $runtime seconds."

# For Ubuntu
# java -cp "atom-1.14.jar:." atomSimulation.Main 200 5 10 100
# javac -cp "atom-1.14.jar:." -d . application/src/atomSimulation/Main.java application/src/atomSimulation/InformedAgent.java application/src/atomSimulation/NoiseAgent.java
