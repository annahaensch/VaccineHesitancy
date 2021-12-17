""" Run Symmetric Simulations.
"""
import sys
sys.path.append('..')

import src as odyn
import logging
import pandas as pd
import os

logging.basicConfig(level=logging.INFO)

def main():

    # Make directory if it doesn't exist.
    isdir = os.path.isdir("../data/sym")
    if isdir == False:
        os.mkdir("../data/sym")
    isdir = os.path.isdir("../data/sym/no_name_county")
    if isdir == False:
        os.mkdir("../data/sym/no_name_county")

    logging.info("Loading SYM geographic data.")


    model = odyn.OpinionNetworkModel(
                                probabilities = [.45,.1,.45],
                                distance_scaling_factor = 1/50,
                                importance_of_weight = 1.3, 
                                importance_of_distance = 2.7,
                                include_weight = True,
                                include_opinion = True
                               )

    model.populate_model(num_agents = 1000, 
                            show_plot = False)
    initial_belief_df = model.belief_df.copy()

    # Save population data.
    model.agent_df.to_parquet("../data/sym/no_name_county/agent_df.pq")
    model.belief_df.to_parquet("../data/sym/no_name_county/belief_df.pq")
    model.prob_df.columns = [str(i) for i in model.prob_df.columns]
    model.prob_df.to_parquet("../data/sym/no_name_county/prob_df.pq")
    model.prob_df.columns = [int(i) for i in model.prob_df.columns]

    model.adjacency_df.columns = [str(i) for i in model.adjacency_df.columns]
    model.adjacency_df.to_parquet("../data/sym/no_name_county/adjacency_df.pq")
    model.adjacency_df.columns = [int(i) for i in model.adjacency_df.columns]

    logging.info("\n Model Loaded.")

    
    # Run simulations for no influencers.
    logging.info("\n Running simulation for no influencers.")
    
    model.left_reach = 0
    model.right_reach = 0
    mega_influencer_df = model.connect_mega_influencers(
    belief_df = initial_belief_df)
    model.mega_influencer_df = mega_influencer_df

    sim = odyn.NetworkSimulation()
    sim.run_simulation(model = model, phases = 60)
    sim.dynamic_belief_df.columns = [str(i) for i in sim.dynamic_belief_df.columns]
    sim.dynamic_belief_df.to_parquet(
        "../data/sym/no_name_county/simulation_results_none.pq")

    # Run simulations for left reach 0,.2,.4,.6,.8,1. with right reach .8.
    reaches = [0,2,4,6,8,10]
    for i in range(len(reaches)):
        r = reaches[i]

        logging.info("\n Running simulation for r = {}".format(r))
        
        model.left_reach = r/10
        model.right_reach = .8
        mega_influencer_df = model.connect_mega_influencers(
        belief_df = initial_belief_df)
        model.mega_influencer_df = mega_influencer_df

        sim = odyn.NetworkSimulation()
        sim.run_simulation(model = model, phases = 60, store_results = False)
        sim.dynamic_belief_df.columns = [str(i) for i in sim.dynamic_belief_df.columns]
        sim.dynamic_belief_df.to_parquet(
            "../data/sym/no_name_county/simulation_results_{}.pq".format(r))

    return None


if __name__ == '__main__':
    main()