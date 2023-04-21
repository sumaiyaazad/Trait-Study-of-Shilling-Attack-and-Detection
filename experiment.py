import argparse
import pandas as pd
import os
import matplotlib.pyplot as plt

from config import *

import utils.notification as noti
from utils.data_loader import *
from utils.similarity_measures import *
from utils.misc import *
from utils.log import Logger
from utils.evaluation import *
from utils.sendmail import *
from attacks.base_attack import *
from attacks.random import *
from attacks.average import *

from recommender_systems.memory_based.item_based_CF import ItemBasedCF
from recommender_systems.memory_based.user_based_CF import UserBasedCF
from recommender_systems.model_based.matrix_factorization_CF import MatrixFactorizationCF



def load_data(dataset, dirname, all_data, all_currentdir, log):
    """
    Load dataset
    param dataset: name of the dataset
    param dirname: directory name
    param all_data: dictionary of all datasets
    param all_currentdir: dictionary of all current directories
    param log: object of Logger class
    """
    
    # ------------------------------------------------------------------------------------------------ load dataset
    if dataset in all_data.keys():
        data = all_data[dataset]
    elif dataset == 'ml-1m':
        data = load_data_ml_1M(split=True)
    elif dataset == 'dummy':
        data = load_data_dummy()
    elif dataset == 'yahoo_movies':
        data = load_data_yahoo_movies(split=True)
    else:
        if args.log:
            log.append('dataset {} not found'.format(dataset))
            log.abort()
        raise ValueError('Dataset not found.')
    if args.log:
        log.append('dataset {} loaded'.format(dataset))
    all_data[dataset] = data

    # create directory for current dataset
    if dataset in all_currentdir.keys():
        currentdir = all_currentdir[dataset]
    else:
        currentdir = dirname + dataset + '/'
        all_currentdir[dataset] = currentdir
    os.makedirs(currentdir, exist_ok=True)

    return all_data, all_currentdir, data, currentdir

def generateRecommendations(train, rs_model, similarity, similarities_dir, recommendation_filename, log, attack_size=None, filler_size=None):
    """
    Generate recommendations for all users in the training set
    param train: training set
    param rs_model: recommender system model
    param similarity: similarity measure
    param similarities_dir: directory to store similarity files
    param recommendation_filename: filename of storing recommendation result
    param log: object of Logger class
    """

    if similarity == 'cosine':
        similarity_function = cosine_similarity
    elif similarity == 'pearson':
        similarity_function = pearson_correlation
    elif similarity == 'jaccard':
        similarity_function = jaccard_similarity
    elif similarity == 'adjusted_cosine':
        similarity_function = adjusted_cosine_similarity
    else:
        if args.log:
            log.append('similarity measure {} not found'.format(similarity))
            log.abort()
        if args.noti_level > 0:
            noti.balloon_tip('SAShA Detection', 'Similarity measure {} not found. Experiment aborted.'.format(similarity))
        raise ValueError('Similarity measure not found.')

    if rs_model == 'ibcf':
        similarity_filename = similarities_dir + 'item_item_' + similarity + ('' if attack_size is None else '_{}'.format(attack_size)) + ('' if filler_size is None else '_{}'.format(filler_size)) + '.csv'

        rs = ItemBasedCF(train, similarity_filename, similarity=similarity_function, notification_level=0, log=log if args.log else None)
        rs.getRecommendationsForAllUsers(n_neighbors=IKNN, verbose=True, output_filename=recommendation_filename, sep=',', top_n=TOP_N)

    elif rs_model == 'ubcf':
        similarity_filename = similarities_dir + 'user_user_' + similarity + ('' if attack_size is None else '_{}'.format(attack_size)) + ('' if filler_size is None else '_{}'.format(filler_size)) + '.csv'

        rs = UserBasedCF(train, similarity_filename, similarity=similarity_function, notification_level=0, log=log if args.log else None)
        rs.getRecommendationsForAllUsers(n_neighbors=UKNN, verbose=True, output_filename=recommendation_filename, sep=',', top_n=TOP_N)

    elif rs_model == 'mfcf':
        train_data, train_users, train_items = train
        mfcf_train_data, mfcf_train_user, mfcf_train_item = convert_to_matrix(train_data, train_users, train_items)

        rs = MatrixFactorizationCF(mfcf_train_data, mfcf_train_user, mfcf_train_item, K=K, alpha=ALPHA, beta=BETA, iterations=MAX_ITER, notification_level=0, log=log if args.log else None)

        rs.train(verbose=True)
        rs.save_recommendations(output_path=recommendation_filename, n=TOP_N, verbose=True)

    else:
        if args.log:
            log.append('recommender system {} not found'.format(rs_model))
            log.abort()
        if args.noti_level > 0:
            noti.balloon_tip('SAShA Detection', 'Recommender system {} not found. Experiment aborted.'.format(rs_model))
        raise ValueError('Recommender system not found.')
    
    # logging is done outside of this function
    pass


def experiment(log, dirname, BREAKPOINT=0):
    """
    Run experiment
    param log: object of Logger class
    param dirname: directory to store experiment results
    """
    print(BREAKPOINT, dirname)

    # return

                        # (experiment start)
    if BREAKPOINT < 1:  # ------------------------------------------------------------------------------------ breakpoint 1

        if args.log:
            
            log.append('\n\n\n')
            log.append('experiment started')
            log.append('dataset: {}'.format(DATASETS))
            log.append('recommender system: {}'.format(RS_MODELS))
            log.append('similarity measure: {}'.format(SIMILARITY_MEASURES))
            log.append('attack: {}'.format(ATTACKS))
            log.append('attack impact evaluation metrics: {}'.format(EVALUATIONS))
            log.append('detection: {}'.format(DETECTIONS))
            log.append('experiment start time: {}'.format(now()))
            log.append('experiment result directory: {}'.format(dirname))
            log.append('Log file: {}'.format(LOG_FILE))
            log.append('\n\n\n')

        if args.send_mail:
            sendmail(SUBJECT, 'Experiment started')


        BREAKPOINT = 1  
        print('BREAKPOINT 1')
        bigskip()
        if args.log:
            log.append('BREAKPOINT 1')
            log.append('\n\n\n')

    else:

        if args.log:
            log.append('experiment resumed from breakpoint {}'.format(BREAKPOINT))
            log.append('dataset: {}'.format(DATASETS))
            log.append('recommender system: {}'.format(RS_MODELS))
            log.append('similarity measure: {}'.format(SIMILARITY_MEASURES))
            log.append('attack: {}'.format(ATTACKS))
            log.append('attack impact evaluation metrics: {}'.format(EVALUATIONS))
            log.append('detection: {}'.format(DETECTIONS))
            log.append('experiment start time: {}'.format(now()))
            log.append('experiment result directory: {}'.format(dirname))
            log.append('Log file: {}'.format(LOG_FILE))
            log.append('\n\n\n')

        if args.send_mail:
            sendmail(SUBJECT, 'Experiment resumed')

        print('BREAKPOINT {}'.format(BREAKPOINT))
        bigskip()
        if args.log:
            log.append('BREAKPOINT {}'.format(BREAKPOINT))
            log.append('\n\n\n')

    ####################################### GLOBAL VARIABLES ############################################
    all_data = {}                                                                                       #      
    all_currentdir = {}                                                                                 #
    #####################################################################################################

                        # (load data, popular and unpopular items, target items similarity)
    if BREAKPOINT < 2:  # ------------------------------------------------------------------------------------ breakpoint 2
        for dataset in DATASETS:
            # load dataset
            all_data, all_currentdir, data, currentdir = load_data(dataset, dirname, all_data, all_currentdir, log)
            
            train, test = data
            train_data, train_users, train_items = train

            # sort items by average rating
            items_sorted = train_data.groupby('item_id')['rating'].mean().to_frame()
            items_sorted.reset_index(inplace=True)
            items_sorted = items_sorted.rename(columns = {'index':'item_id', 'rating':'avg_rating'})
            items_sorted = items_sorted.sort_values(by=['avg_rating'], ascending=False)
            items_sorted.reset_index(inplace=True)
            items_sorted = items_sorted.drop(columns=['index'])

            # list most popular items
            popular_items = items_sorted.head(NUM_TARGET_ITEMS)
            popular_items.to_csv(currentdir + '{}_popular_items.csv'.format(NUM_TARGET_ITEMS), index=False)
            print('generated {} popular items for dataset {}'.format(NUM_TARGET_ITEMS, dataset))
            if args.log:
                log.append('generated {} popular items for dataset {}. Saved in file {}'.format(NUM_TARGET_ITEMS, dataset, currentdir + '{}_popular_items.csv'.format(NUM_TARGET_ITEMS)))

            # list most unpopular items; to be used lates as target items of push attacks
            unpopular_items = items_sorted.tail(NUM_TARGET_ITEMS).iloc[::-1]
            unpopular_items.to_csv(currentdir + '{}_unpopular_items.csv'.format(NUM_TARGET_ITEMS), index=False)
            print('generated {} unpopular items for dataset {}'.format(NUM_TARGET_ITEMS, dataset))
            if args.log:
                log.append('generated {} unpopular items for dataset {}. Saved in file {}'.format(NUM_TARGET_ITEMS, dataset, currentdir + '{}_unpopular_items.csv'.format(NUM_TARGET_ITEMS)))


            # generate list of items similar to target items (unpopular) using knowledge graph
            target_items = unpopular_items['item_id'].tolist()

            # create directory for storing similarities
            target_similar_dir = currentdir + 'similar_items_target/'
            os.makedirs(target_similar_dir, exist_ok=True)
            

        BREAKPOINT = 2
        print('BREAKPOINT 2')
        bigskip()
        if args.log:
            log.append('BREAKPOINT 2')
            log.append('\n\n\n')

# so far, we have generated the most popular and unpopular items for the dataset
# now, we will generate pre-attack recommendations for each recommender system

                        # (generate pre-attack recommendations)
    if BREAKPOINT < 3:  # ------------------------------------------------------------------------------------ breakpoint 3 
        for dataset in DATASETS:
            # load dataset
            all_data, all_currentdir, data, currentdir = load_data(dataset, dirname, all_data, all_currentdir, log)
            
            train, test = data
            train_data, train_users, train_items = train

            # create directory for storing similarities
            pre_attack_similarities_dir = currentdir + 'similarities/pre_attack/'
            os.makedirs(pre_attack_similarities_dir, exist_ok=True)
            if args.log:
                log.append('created directory {}'.format(pre_attack_similarities_dir))

            post_attack_similarities_dir = currentdir + 'similarities/post_attack/'
            os.makedirs(post_attack_similarities_dir, exist_ok=True)
            if args.log:
                log.append('created directory {}'.format(post_attack_similarities_dir))

            post_detection_similarities_dir = currentdir + 'similarities/post_detection/'
            os.makedirs(post_detection_similarities_dir, exist_ok=True)
            if args.log:
                log.append('created directory {}'.format(post_detection_similarities_dir))

            for similarity in SIMILARITY_MEASURES:
                for rs_model in RS_MODELS:

                    # generate pre-attack recommendations ---------------------------------------------------------------------------------------
                    recommendations_dir = currentdir + rs_model + '/recommendations/'
                    os.makedirs(recommendations_dir, exist_ok=True)

                    print('Generating pre-attack recommendations for {} with {} similarity for dataset {}'.format(rs_model, similarity, dataset))
                    if args.log:
                        log.append('Generating pre-attack recommendations for {} with {} similarity for dataset {}'.format(rs_model, similarity, dataset))


                    pre_attack_recommendations_filename = recommendations_dir + 'pre_attack_{}_recommendations.csv'.format(similarity)
                    generateRecommendations(train=train, 
                                            rs_model=rs_model, 
                                            similarity=similarity, 
                                            similarities_dir=pre_attack_similarities_dir, recommendation_filename=pre_attack_recommendations_filename, 
                                            log=log)
                    
                    print('Pre-attack recommendations for {} with {} similarity for dataset {} generated'.format(rs_model, similarity, dataset))
                    if args.log:
                        log.append('Pre-attack recommendations for {} with {} similarity for dataset {} generated'.format(rs_model, similarity, dataset))

                    if args.send_mail:
                        sendmail(SUBJECT, 'Pre-attack recommendations for generated.\nDataset: {}\nRS: {}\nSimilarity: {}\n'.format(dataset, rs_model, similarity))

                    if args.noti_level > 0:
                        noti.balloon_tip('SAShA Detection', 'Pre-attack recommendations for {} generated'.format(rs_model))

        BREAKPOINT = 3  
        print('BREAKPOINT 3')
        bigskip()
        if args.log:
            log.append('BREAKPOINT 3')
            log.append('\n\n\n')


# so far we have generated pre-attack recommendations for each recommender system
# now, we will calculate the hit ratio of the pre-attack recommendations

                        # (calculate hit ratio of pre-attack recommendations)
    if BREAKPOINT < 4:  # ------------------------------------------------------------------------------------ breakpoint 4 
        for dataset in DATASETS:
            
            if dataset in all_currentdir.keys():
                currentdir = all_currentdir[dataset]
            else:
                currentdir = dirname + dataset + '/'
                all_currentdir[dataset] = currentdir

            for similarity in SIMILARITY_MEASURES:
                for rs_model in RS_MODELS:

                    # calculate hit ratio of pre-attack recommendations ---------------------------------------------------------------------------------------
                    recommendations_dir = currentdir + rs_model + '/recommendations/'
                    hit_ratio_dir = currentdir + rs_model + '/results/' + 'hit_ratio/'
                    os.makedirs(hit_ratio_dir, exist_ok=True)

                    print('Calculating hit ratio of pre-attack recommendations for {} with {} similarity for dataset {}'.format(rs_model, similarity, dataset))
                    if args.log:
                        log.append('Calculating hit ratio of pre-attack recommendations for {} with {} similarity for dataset {}'.format(rs_model, similarity, dataset))

                    # load target items
                    target_items = pd.read_csv(currentdir + '{}_unpopular_items.csv'.format(NUM_TARGET_ITEMS))
                    target_items.columns = ['item_id', 'avg_rating']
                    target_items = target_items['item_id'].tolist()

                    pre_attack_recommendations_filename = recommendations_dir + 'pre_attack_{}_recommendations.csv'.format(similarity)
                    pre_attack_hit_ratio = hit_ratio(recommendations_filename = pre_attack_recommendations_filename,
                                                    target_items = target_items,
                                                    among_firsts=TOP_Ns,
                                                    log = log)
                    
                    pre_attack_hit_ratio.to_csv(hit_ratio_dir + 'pre_attack_{}_hit_ratio.csv'.format(similarity), index=False)
                    print('Hit ratio of pre-attack recommendations for {} with {} similarity for dataset {} calculated'.format(rs_model, similarity, dataset))
                    if args.log:
                        log.append('Hit ratio of pre-attack recommendations for {} with {} similarity for dataset {} calculated'.format(rs_model, similarity, dataset))

        if args.send_mail:
            sendmail(SUBJECT, 'Hit ratio of pre-attack recommendations calculated.')

        BREAKPOINT = 4  
        print('BREAKPOINT 4')
        bigskip()
        if args.log:
            log.append('BREAKPOINT 4')
            log.append('\n\n\n')

# so far we have calculated the hit ratio of pre-attack recommendations
# now, we will generate attack profiles

                        # (generate attack profiles)
    if BREAKPOINT < 5:  # ------------------------------------------------------------------------------------ breakpoint 5
        for dataset in DATASETS:
            all_data, all_currentdir, data, currentdir = load_data(dataset, dirname, all_data, all_currentdir, log)
            
            train, test = data
            train_data, train_users, train_items = train

            for attack in ATTACKS:
                
                attack_dir = currentdir + 'attack_profiles/' + attack + '/'
                os.makedirs(attack_dir, exist_ok=True)
                R_MIN, R_MAX = rating_range[dataset]


                for attack_size in ATTACK_SIZES:
                    for filler_size in FILLER_SIZES:

                        # launch attacks ---------------------------------------------------------------------------------------

                        print('Generating {} attack profiles with attack size {} and filler size {} for dataset {}'.format(attack, attack_size, filler_size, dataset))
                        if args.log:
                            log.append('Generating {} attack profiles with attack size {} and filler size {} for dataset {}'.format(attack, attack_size, filler_size, dataset))

                        # load target items
                        target_items = pd.read_csv(currentdir + '{}_unpopular_items.csv'.format(NUM_TARGET_ITEMS))
                        target_items.columns = ['item_id', 'avg_rating']
                        target_items = target_items['item_id'].tolist()

                        # create attack object
                        if attack == 'random':
                            attack_generator = RandomAttack(train_data, R_MAX, R_MIN, attack_size, filler_size)
                        elif attack == 'average':
                            attack_generator = AverageAttack(train_data, R_MAX, R_MIN, attack_size, filler_size)
                        else:
                            raise ValueError('Attack not found.')


                        # generate attack profiles
                        # for target_id in tqdm(target_items):
                        #     # {target_id}_{attack size}_{filler size}.csv (e.g. random_100_100.csv)
                        #     attack_profiles_filename = attack_dir + '{}_{}_{}.csv'.format(target_id, attack_size, filler_size)

                        #     attack_generator.generate_profile(target_id, 0, attack_profiles_filename)
                            # ISSUE: attack_generator.generate_profile() takes 1 target item at a time, but we want to take multiple target items at a time FIXED

                        # generate attack profiles
                        attack_profiles_filename = attack_dir + 'shilling_profiles_{}_{}.csv'.format(attack_size, filler_size)
                        attack_generator.generate_profile(target_items, 0, attack_profiles_filename)
                    
                        print('{} attack profiles with attack size {} and filler size {} for dataset {} generated'.format(attack, attack_size, filler_size, dataset))
                        if args.log:
                            log.append('{} attack profiles with attack size {} and filler size {} for dataset {} generated'.format(attack, attack_size, filler_size, dataset))

                        

        if args.send_mail:
            sendmail(SUBJECT, 'All attack profiles generated.')
        
        BREAKPOINT = 5
        print('BREAKPOINT 5')
        bigskip()
        if args.log:
            log.append('BREAKPOINT 5')
            log.append('\n\n\n')

# so far we have generated attack profiles
# now, we will generate post-attack recommendations for fixed attack_size and fixed filler_size

                        # (generate post-attack recommendations)
    if BREAKPOINT < 6:  # ------------------------------------------------------------------------------------ breakpoint 6
        for dataset in DATASETS:
            all_data, all_currentdir, data, currentdir = load_data(dataset, dirname, all_data, all_currentdir, log)
            
            train, test = data
            train_data, train_users, train_items = train

            for similarity in SIMILARITY_MEASURES:
                for rs_model in RS_MODELS:
                    for attack in ATTACKS:
                        for attack_size in ATTACK_SIZES:
                            for filler_size in FILLER_SIZES:

                                if (attack_size != ATTACK_SIZE_PERCENTAGE) and (filler_size != FILLER_SIZE_PERCENTAGE):
                                    continue

                                # fetch target items
                                target_items = pd.read_csv(currentdir + '{}_unpopular_items.csv'.format(NUM_TARGET_ITEMS))
                                target_items.columns = ['item_id', 'avg_rating']
                                target_items = target_items['item_id'].tolist()

                                # fetch attack profiles for all target items
                                attack_dir = currentdir + 'attack_profiles/' + attack + '/'
                                attack_profiles = pd.DataFrame()
                                attack_profile = pd.read_csv(attack_dir + 'shilling_profiles_{}_{}.csv'.format(attack_size, filler_size))
                                attack_profiles = pd.concat([attack_profiles, attack_profile], ignore_index=True)
                                attack_profiles = attack_profiles[['user_id', 'item_id', 'rating']]
                                attack_profiles.columns = ['user_id', 'item_id', 'rating']

                                # concat attack data with train data
                                new_train_data = pd.concat([train_data, attack_profiles], ignore_index=True)
                                
                                # concat attack users with train users
                                temp = pd.DataFrame(attack_profiles.user_id.unique())
                                temp.columns = ['user_id']
                                new_train_users = train_users.copy()
                                new_train_users = pd.concat([new_train_users, temp], ignore_index=True)

                                # similarity files directory and filenames defination
                                similarity_dir = currentdir + 'similarities/' + 'post_attack/' + attack + '/'
                                os.makedirs(similarity_dir, exist_ok=True)

                                # recommendations directory and filenames defination
                                recommendations_dir = currentdir + rs_model + '/recommendations/' + attack + '/'
                                os.makedirs(recommendations_dir, exist_ok=True)
                                recommendations_filename = recommendations_dir + 'post_attack_{}_{}_{}_recommendations.csv'.format(similarity, attack_size, filler_size)

                                # generate post-attack recommendations
                                print('Generating post-attack recommendations for dataset {}, similarity measure {}, recommender system {}, attack {}, attack size {}, filler size {}'.format(dataset, similarity, rs_model, attack, attack_size, filler_size))
                                if args.log:
                                    log.append('Generating post-attack recommendations for dataset {}, similarity measure {}, recommender system {}, attack {}, attack size {}, filler size {}'.format(dataset, similarity, rs_model, attack, attack_size, filler_size))


                                generateRecommendations((new_train_data, new_train_users, train_items),
                                                        rs_model,
                                                        similarity,
                                                        similarity_dir,
                                                        recommendations_filename,
                                                        log,
                                                        attack_size,
                                                        filler_size)

                                # print('Post-attack recommendations generated for dataset {}, similarity measure {}, recommender system {}, attack {}, attack size {}, filler size {}'.format(dataset, similarity, rs_model, attack, attack_size, filler_size))
                                # if args.log:
                                #     log.append('Post-attack recommendations generated for dataset {}, similarity measure {}, recommender system {}, attack {}, attack size {}, filler size {}'.format(dataset, similarity, rs_model, attack, attack_size, filler_size))
                                # if args.send_mail:
                                #     sendmail(SUBJECT, 'Post-attack recommendations generated for dataset {}, similarity measure {}, recommender system {}, attack {}, attack size {}, filler size {}'.format(dataset, similarity, rs_model, attack, attack_size, filler_size))

                    print('Post attack Recommendations generated for dataset {}, similarity measure {}, recommender system {}'.format(dataset, similarity, rs_model))
                    if args.send_mail:
                        sendmail(SUBJECT, 'Post attack Recommendations generated for dataset {}, similarity measure {}, recommender system {}'.format(dataset, similarity, rs_model))


        BREAKPOINT = 6
        print('BREAKPOINT 6')
        bigskip()
        if args.log:
            log.append('BREAKPOINT 6')
            log.append('\n\n\n')

# so far we have generated post-attack recommendations
# now, we will calculate hit ratio and generate graphs

                        # (calculate hit ratio and generate graphs)
    if BREAKPOINT < 7:  # ------------------------------------------------------------------------------------ breakpoint 7
        for dataset in DATASETS:
            if dataset in all_currentdir.keys():
                currentdir = all_currentdir[dataset]
            else:
                currentdir = dirname + dataset + '/'
                all_currentdir[dataset] = currentdir

            for similarity in SIMILARITY_MEASURES:
                for rs_model in RS_MODELS:

                    # calculate hit ratio of post-attack recommendations ---------------------------------------------------------------------------------------
                    recommendations_dir = currentdir + rs_model + '/recommendations/'
                    hit_ratio_dir = currentdir + rs_model + '/results/' + 'hit_ratio/'
                    os.makedirs(hit_ratio_dir, exist_ok=True)

                    print('Calculating hit ratio of post-attack recommendations for {} with {} similarity for dataset {}'.format(rs_model, similarity, dataset))
                    if args.log:
                        log.append('Calculating hit ratio of post-attack recommendations for {} with {} similarity for dataset {}'.format(rs_model, similarity, dataset))

                    # load target items
                    target_items = pd.read_csv(currentdir + '{}_unpopular_items.csv'.format(NUM_TARGET_ITEMS))
                    target_items.columns = ['item_id', 'avg_rating']
                    target_items = target_items['item_id'].tolist()

                    # for every attack, attack size and filler size, calculate hit ratio 
                    # concatenate in one dataframe and save to csv
                    
                    
                    hit_ratios = pd.DataFrame(columns = ['attack', 'attack_size', 'filler_size', 'hit_ratio'])

                    for attack in ATTACKS:
                        for attack_size in ATTACK_SIZES:
                            for filler_size in FILLER_SIZES:

                                if (attack_size != ATTACK_SIZE_PERCENTAGE) and (filler_size != FILLER_SIZE_PERCENTAGE):
                                    continue

                                post_attack_recommendations_filename = recommendations_dir + attack + '/post_attack_{}_{}_{}_recommendations.csv'.format(similarity, attack_size, filler_size)
                                post_attack_hit_ratio = hit_ratio(recommendations_filename = post_attack_recommendations_filename,
                                                                target_items = target_items,
                                                                among_firsts=TOP_Ns,
                                                                log = log)
                                post_attack_hit_ratio['attack'] = attack
                                post_attack_hit_ratio['attack_size'] = attack_size
                                post_attack_hit_ratio['filler_size'] = filler_size
                                hit_ratios = pd.concat([hit_ratios, post_attack_hit_ratio], ignore_index=True)


                    hit_ratio_filename = hit_ratio_dir + 'post_attack_{}_hit_ratio.csv'.format(similarity)
                    hit_ratios.to_csv(hit_ratio_filename, index=False)

                    if args.log:
                        log.append('Hit ratio of post-attack recommendations calculated for {} with {} similarity for dataset {}'.format(rs_model, similarity, dataset))
                        log.append('Hit ratio of post-attack recommendations saved to {}'.format(hit_ratio_filename))

                    print('Hit ratio of post-attack recommendations calculated for {} with {} similarity for dataset {}'.format(rs_model, similarity, dataset))

                    # generate graphs   hit ratio vs attack size, fixed filler size
                    if args.log:
                        log.append('Generating graphs for hit ratio vs attack size, fixed filler size for {} with {} similarity for dataset {}'.format(rs_model, similarity, dataset))

                    graph_dir = currentdir + rs_model + '/graphs/'
                    os.makedirs(graph_dir, exist_ok=True)
                    
                    attack_size_hit_ratios = hit_ratios[hit_ratios['filler_size'] == FILLER_SIZE_PERCENTAGE]
                    for attack in ATTACKS:
                        graph_filename = graph_dir + '{}_attack_size_vs_hit_ratio.png'.format(attack)

                        # filter hit ratios for current attack
                        attack_hit_ratio = attack_size_hit_ratios[attack_size_hit_ratios['attack'] == attack]

                        for top_n in TOP_Ns:
                            # filter hit ratios for current top_n
                            current_hit_ratios_for_topn = attack_hit_ratio[attack_hit_ratio['among_first'] == top_n]  # top_n is  among_first
                            plt.plot(ATTACK_SIZES, current_hit_ratios_for_topn['hit_ratio'].to_list(), label='top {}'.format(top_n))
                        plt.axis('tight')
                        plt.legend()
                        plt.title('{} attack, {} similarity, filler size {}'.format(attack, similarity, FILLER_SIZE_PERCENTAGE))
                        plt.xlabel('Attack size')
                        plt.ylabel('Hit ratio')
                        plt.savefig(graph_filename)
                        plt.clf()


                    # generate graphs   hit ratio vs filler size, fixed attack size
                    if args.log:
                        log.append('Generating graphs for hit ratio vs filler size, fixed attack size for {} with {} similarity for dataset {}'.format(rs_model, similarity, dataset))
                    filler_hit_ratios = hit_ratios[hit_ratios['attack_size'] == ATTACK_SIZE_PERCENTAGE]
                    for attack in ATTACKS:
                        graph_filename = graph_dir + '{}_filler_size_vs_hit_ratio.png'.format(attack)

                        # filter hit ratios for current attack
                        current_hit_ratios = filler_hit_ratios[filler_hit_ratios['attack'] == attack]

                        for top_n in TOP_Ns:
                            # filter hit ratios for current top_n
                            current_hit_ratios_for_topn = current_hit_ratios[current_hit_ratios['among_first'] == top_n]  # top_n is  among_first

                            plt.plot(FILLER_SIZES, current_hit_ratios_for_topn['hit_ratio'].to_list(), label='top {}'.format(top_n))
                        plt.axis('tight')
                        plt.legend()
                        plt.title('{} attack, {} similarity, attack size {}'.format(attack, similarity, ATTACK_SIZE_PERCENTAGE))
                        plt.xlabel('Filler size')
                        plt.ylabel('Hit ratio')
                        plt.savefig(graph_filename)
                        plt.clf()

        if args.send_mail:
            sendmail(SUBJECT, 'Evaluations done for post-attack recommendations')

        BREAKPOINT = 7
        print('BREAKPOINT 7')
        bigskip()
        if args.log:
            log.append('BREAKPOINT 7')
            log.append('\n\n\n')

# so far, we have calculated hit ratio for post-attack recommendations
# now, we will calculate hit ratio for post-detection recommendations

    pass




                    

def main():

    # ------------------------------------------- define experiment environment -------------------------------------------
    print('------------------------------------------- Experiment Environment -------------------------------------------')
    print('Dataset: ', DATASETS)
    print('Recommender system: ', RS_MODELS)
    print('Similarity measure: ', SIMILARITY_MEASURES)
    print('Attack: ', ATTACKS)
    print('Attack impact evaluation metrics: ', EVALUATIONS)
    print('Detection: ', DETECTIONS)
    print('Experiment start time: ', now())

    # experiment result directory
    
    try:
        next_version = np.array([int(name[len('experiment_results_'):]) for name in os.listdir(OUTDIR) if os.path.isdir(os.path.join(OUTDIR, name)) and name.startswith('experiment_results_')]).max() + 1
    except ValueError:
        next_version = 1

    BREAKPOINT = 0
    if args.breakpoint > 0:
        next_version = args.version
        BREAKPOINT = args.breakpoint

    dirname = OUTDIR + 'experiment_results_' + str(next_version) + '/'
    print('Experiment result directory: ', dirname)
    os.makedirs(dirname, exist_ok=True)
    bigskip()

    if args.log:
        LOG_FILE = dirname + 'log.txt'
        log = Logger(LOG_FILE)


    # ------------------------------------------ starting experiment ------------------------------------------
    try:
        experiment(log, dirname, BREAKPOINT)
    except Exception as e:
        if args.log:
            log.append('experiment failed')
            log.append('error: {}'.format(e))
            log.abort()
        
        if args.send_mail:
            email_body = 'Experiment failed.\r\nError: {}'.format(e)
            sendmailwithfile(SUBJECT, email_body, 'log.txt', LOG_FILE)

        if args.noti_level > 0:
            noti.balloon_tip('SAShA Detection', 'Experiment failed. Error: {}'.format(e))
        raise e
    
    # ------------------------------------------ experiment finished ------------------------------------------

    print('experiment finished')
    
    if args.log:
        log.append('experiment finished')
    
    if args.send_mail:
        sendmailwithfile(subject=SUBJECT, message='Experiment finished Successfully. Results are saved in {}'.format(dirname), filelocation=LOG_FILE, filename='log.txt')
    
    if args.noti_level > 0:
        noti.balloon_tip('SAShA Detection', 'Experiment finished. Results are saved in {}'.format(dirname))
                


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose', type=bool, default=True, help='verbose mode')
    parser.add_argument('--noti_level', type=int, default=0, help='notification level, 0: no notification, 1: only at the end, 2: at verbose mode')
    parser.add_argument('--log', type=bool, default=True, help='log mode')
    parser.add_argument('--breakpoint', type=int, default=0, help='breakpoint, 0: no breakpoint, else: left off at breakpoint')
    parser.add_argument('--version', type=int, default=0, help='experiment version, 0: new experiment, else: old experiment version number')

    parser.add_argument('--send_mail', action='store_true')
    parser.add_argument('--dont_mail', dest='send_mail', action='store_false')
    parser.set_defaults(send_mail=True)

    args = parser.parse_args()

    main()


