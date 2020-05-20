
import time
import requests
from nltk.tokenize import sent_tokenize

from transformer_utilities import *
from dona_custome_responses import *
from aware_embed import *
from stateful import *
from stateful_utils import *

sleep = True
sleep_time = 2

# This is a Facade pattern design in which the model of the MVC is a Facade of
# two classes: awareness and statefulness. It also has a transformer generator

# Globals to restor the checkpoint of the transformer
d_model = 256
num_layers = 2
num_heads = 16
dff = 512
dropout_rate = 0.1

# Where is the checkpoint and data source for tokenizer
checkpoint_path = "./assets/train"
matchCutoff = 0.9
dataset_input_df_name = "actions_reactions_nodup.csv"


class Respond:
    def __init__(self):

        # Load data for everything but the transformer operation
        self.actions, self.reactions, self.awareness, self.awareness_resp = load_data()

        # Load data for the transformer operation
        self.trans_actions, self.trans_reactions, self.trans_awareness, self.trans_awareness_resp = create_save_csv_nodup(
            dataset_input_df_name)
        print(len(self.trans_actions), len(self.trans_reactions), len(
            self.trans_awareness), len(self.trans_awareness_resp))
        # Make a tokenizer using tfds for both actions and reactions
        self.tokenizer = tfds.features.text.SubwordTextEncoder.build_from_corpus(
            self.trans_actions + self.trans_reactions, target_vocab_size=2**13)
        # Define start and end token to indicate the start and end of a sentence
        self.START_TOKEN, self.END_TOKEN = [
            self.tokenizer.vocab_size], [self.tokenizer.vocab_size + 1]
        # Vocabulary size plus start and end token
        self.VOCAB_SIZE = self.tokenizer.vocab_size + 2
        print(type(self.tokenizer.vocab_size))
        print(self.tokenizer.vocab_size)
        print(type(self.VOCAB_SIZE))
        print(self.VOCAB_SIZE)
        # Setup your transformer andrestore the checkpoint
        self.transformer = Transformer(num_layers, d_model, num_heads, dff,
                                       self.VOCAB_SIZE, self.VOCAB_SIZE,
                                       pe_input=self.VOCAB_SIZE,
                                       pe_target=self.VOCAB_SIZE,
                                       rate=dropout_rate)

        self.restore_checkpoint()

        # Awareness instance
        self.awareness_inst = Awareness()
        print("Awareness and embedding instance is instantiated.")

        # Statefulness instance
        self.statefulness_inst = Statefulness()
        print("statefulness_inst created.")

    def restore_checkpoint(self):
        # Restor the checkpoint
        ckpt = tf.train.Checkpoint(
            transformer=self.transformer, optimizer=optimizer)
        ckpt_manager = tf.train.CheckpointManager(
            ckpt, checkpoint_path, max_to_keep=5)
        # if a checkpoint exists, restore the latest checkpoint.
        if ckpt_manager.latest_checkpoint:
            ckpt.restore(ckpt_manager.latest_checkpoint)
            print ('Latest checkpoint restored!!')

    def get_a_response(self, query):
        # we check existence, if it exists, we post it, if not we get the best match and the extent_knowledge from embedder and the awareness on the query.
        # w versus !world and cross_product is < extent_knowledge or >= extent_knowledge:
        # extentmatch >= matchCutoff and (w and !w), so awareness is irrelevant
        # extentmatch < matchCutoff and w, negative_world_responses
        # < matchCutoff and !w, generate
        # awearenss_response = 'w', negative_general_responses
        # awearenss_response = '!w', post generated
        if(query in self.actions):
            query_index = self.actions.index(query)
            response = self.reactions[query_index]
            aware = self.awareness[query_index]
            print("Response is known ahead.")
            best_match = -1
        else:
            print("query now is: " + query)
            max_index, extentmatch = self.awareness_inst.get_most_similar(
                query)
            print("extentmatch is: " + str(extentmatch))
            aware = self.awareness_inst.get_awareness_query(query)

            if extentmatch >= matchCutoff:
                best_match = max_index
                print("extentmatch >= matchCutoff")
                response = self.reactions[best_match]
            else:
                if aware == 'w':
                    print("extentmatch < matchCutoff and aware = 'w'")
                    best_match = -2
                    response = negative_world_responses[np.random.choice(
                        len(negative_world_responses))]
                else:
                    print("extentmatch < matchCutoff and aware != 'w'")
                    best_match = -3
                    response = generate(
                        query, self.tokenizer, self.transformer)
                    response_aware = self.awareness_inst.get_awareness_response(
                        response)
                    if response_aware != 'w':
                        if response not in self.reactions and best_match == -3:
                            best_match = -4
                            print('Dona generated this response from scratch!')
                    if response_aware == 'w':
                        print(
                            "extentmatch < matchCutoff and aware != 'w' and response_aware == 'w'")
                        best_match = -5
                        response = negative_general_responses[np.random.choice(
                            len(negative_general_responses))]

        return response, aware, best_match

    def cognify(self, query, this_user, this_user_info, this_user_interactions):

        # Use awareness instance along with generator and embedder
        response, aware, best_match = self.get_a_response(query)
        #print(response + " :before statefulness")
        #print(awareness + " :before statefulness")

        # Get final response and satatefulness, pass best_match and awareness to statefulness
        stateful_response, stateful = self.statefulness_inst.statefulness(
            query, response, this_user, this_user_info, this_user_interactions)

        #print(stateful_response + " :after checking statefulness")
        #print('statefulness is: ' + str(stateful))

        # Class-4 statefulness uses get_a_response() which is not in stateful
        # and must be here
        if stateful == 4:
            # We need some preprocessing here!
            print("class 4 detected in respond after self.statefulness_inst.statefulness")
            list_of_sents = sent_tokenize(stateful_response)
            for n in range(len(list_of_sents)):
                if "?" in list_of_sents[n]:
                    if "," in list_of_sents[n]:
                        pos = list_of_sents[n].find(',')
                        list_of_sents[n] = list_of_sents[n][pos +
                                                            1:len(list_of_sents[n])]
                    stateful_response = list_of_sents[n]

            query1 = stateful_response.lower()
            print("query1 is: " + query1)
            max_index, extentmatch = self.awareness_inst.get_most_similar(
                query1)
            stateful_response = self.reactions[max_index]
            print("stateful_response before replacements: " + stateful_response)
            stateful_response = simple_replacements(
                this_user, this_user_info, query1, stateful_response)
            print("stateful_response after replacements: " + stateful_response)
            for n in stateful_class_4_phrases_checks:
                if n in stateful_response:
                    stateful_response = stateful_response.replace(n, " ")

        # This is to cover for lack of response

        if stateful_response is None or 'statefulresponse' in stateful_response:
            stateful_response = negative_general_responses[np.random.choice(
                len(negative_general_responses))]

        if "Undisclosed" in stateful_response:
            stateful_response = negative_world_responses[np.random.choice(
                len(negative_world_responses))]

        if sleep:
            time.sleep(sleep_time)
        print(best_match)
        return stateful_response, aware, stateful, best_match
