#normalise scores function
def normalise(scores_dict):
    #list scores
    values = list(scores_dict.values())
    #get min and max
    min_val, max_val = min(values), max(values)
    #return normalised
    return {
        key: (val - min_val) / (max_val - min_val) if max_val != min_val else 0
        for key, val in scores_dict.items()
    }

#viability score computation
def calc_viability(rosi_scores, shapley_scores, optimiser_selected_controls, w1=1/3, w2=1/3, w3=1/3):
    #normalise rosi and shapley values
    n_rosi = normalise(rosi_scores)
    n_shapley = normalise(shapley_scores)

    #get optimiser scores in binary by present in selected controls 1 or 0 for excluded in output set
    optimiser_scores = {
        ctrl: 1 if (ctrl, 1) in optimiser_selected_controls else 0
        for ctrl in rosi_scores.keys()
    }

    #get viability scores * weights
    viability_scores = {
        ctrl: w1 * n_rosi.get(ctrl, 0) +
              w2 * n_shapley.get(ctrl, 0) +
              w3 * optimiser_scores.get(ctrl, 0)
        for ctrl in rosi_scores.keys()
    }

    #return viablity scores
    return viability_scores