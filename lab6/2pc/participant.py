import random
import logging

# coordinator messages
from const2PC import VOTE_REQUEST, GLOBAL_COMMIT, GLOBAL_ABORT, PREPARE_COMMIT
# participant decissions
from const2PC import LOCAL_SUCCESS, LOCAL_ABORT
# participant messages
from const2PC import VOTE_COMMIT, VOTE_ABORT, ADOPTED_STATE, VALID_STATE, READY_COMMIT
# misc constants
from const2PC import CLIENT_TIMEOUT

import stablelog


class Participant:
    """
    Implements a two phase commit participant.
    - state written to stable log (but recovery is not considered)
    - in case of coordinator crash, participants mutually synchronize states
    - system blocks if all participants vote commit and coordinator crashes
    - allows for partially synchronous behavior with fail-noisy crashes
    """

    def __init__(self, chan):
        self.channel = chan
        self.participant = self.channel.join('participant')
        self.stable_log = stablelog.create_log(
            "participant-" + self.participant)
        self.logger = logging.getLogger("vs2lab.lab6.2pc.Participant")
        self.coordinator = {}
        self.all_participants = {}
        self.state = 'NEW'

    @staticmethod
    def _do_work():
        # Simulate local activities that may succeed or not
        #return LOCAL_ABORT if random.random() > 2/3 else LOCAL_SUCCESS
        return LOCAL_SUCCESS

    def _enter_state(self, state):
        self.stable_log.info(state)  # Write to recoverable persistant log file
        self.logger.info("Participant {} entered state {}."
                         .format(self.participant, state))
        self.state = state

    def init(self):
        self.channel.bind(self.participant)
        self.coordinator = self.channel.subgroup('coordinator')
        self.all_participants = self.channel.subgroup('participant')
        self._enter_state('INIT')  # Start in local INIT state.

    def run(self):
        # Wait for start of joint commit
        msg = self.channel.receive_from(self.coordinator, CLIENT_TIMEOUT)

        if not msg:  # Crashed coordinator - give up entirely
            if self.state == 'INIT':
                self._enter_state('ABORT')
                return "Participant aborted in INIT because the coordinator crashed."
            return self.determineCoordinator()
             
            

        else:  # Coordinator requested to vote, joint commit starts
            assert msg[1] == VOTE_REQUEST

            # Firstly, come to a local decision
            decision = self._do_work()  # proceed with local activities
            
            # if random.random() > 0.5:  # simulate a crash when Coordinator is in State WAIT
            #    return "Participant {} crashed in state INIT.".format(self.participant)

            # If local decision is negative,
            # then vote for abort and quit directly
            if decision == LOCAL_ABORT:
                self.channel.send_to(self.coordinator, VOTE_ABORT)

            # If local decision is positive,
            # we are ready to proceed the joint commit
            else:
                assert decision == LOCAL_SUCCESS
                self._enter_state('READY')

                # Notify coordinator about local commit vote
                self.channel.send_to(self.coordinator, VOTE_COMMIT)
                
                # if random.random() > 0.5:  # simulate a crash when Coordinator is in State READY
                #     return "Participant {} crashed in state READY.".format(self.participant)

                # Wait for coordinator to notify the final outcome
                msg = self.channel.receive_from(self.coordinator, CLIENT_TIMEOUT)

                if not msg:  # Crashed coordinator
                    return self.determineCoordinator()
                    

                else:  # Coordinator came to a decision
                    decision = msg[1]

        # Change local state based on the outcome of the joint commit protocol
        # Note: If the protocol has blocked due to coordinator crash,
        # we will never reach this point
        if decision == PREPARE_COMMIT:
            self._enter_state('PRECOMMIT')
            if random.random() > 0.5:  # simulate a crash when Coordinator is in State PRECOMMIT
                return "Participant {} crashed in state PRECOMMIT.".format(self.participant)
            self.channel.send_to(self.coordinator, READY_COMMIT)
            
            
            
            
        else:
            assert decision in [GLOBAL_ABORT, LOCAL_ABORT]
            self._enter_state('ABORT')
            return "Participant {} terminated in state {} due to {}.".format(
            self.participant, self.state, decision)
        
        msg = self.channel.receive_from(self.coordinator, CLIENT_TIMEOUT)
        if not msg:  # Crashed coordinator
            return self.determineCoordinator()
            
        else:  # Coordinator came to a decision
            decision = msg[1]
            assert decision in [GLOBAL_COMMIT]
            self._enter_state('COMMIT')
            return "Participant {} terminated in state {} due to {}.".format(
            self.participant, self.state, decision)
      
    def determineCoordinator(self):
            min = 1000000
            id = self.participant
            for participant in self.all_participants:
                if int(participant) < int(min):
                    min = participant
            self.logger.info("Participant {}: Old coordinator was {}.".format(id, self.coordinator))
            self.coordinator={min}
            self.logger.info("Participant {}: New coordinator is {}.".format(id, self.coordinator))
            self.all_participants.remove(min)
            if self.coordinator == {id}:
                self.logger.debug("Coordinator {} send state {} to {}.".format(id, self.state, self.all_participants))
                self.channel.send_to(self.all_participants, self.state)
                
                yet_to_receive = list(self.all_participants)
                while len(yet_to_receive) > 0:
                    msg = self.channel.receive_from(self.all_participants, CLIENT_TIMEOUT)
                    if (not msg):
                        return ("Coordinator {} terminated in state {} due to a timeout.".format(id, self.state))
                    else:
                        self.logger.debug("Coordinator {} received {} from {}.".format(id, msg[1], msg[0]))
                        assert msg[1] == VALID_STATE or msg[1]==ADOPTED_STATE
                        yet_to_receive.remove(msg[0])
                        
                    
                match self.state:
                    case "ABORT":
                        return ("Coordinator {} terminated in state {} due to {}".format(id, self.state, "GLOBAL_ABORT"))
                    case "COMMIT":
                        return ("Coordinator {} terminated in state {} due to {}".format(id, self.state, "GLOBAL_COMMIT"))
                    case "INIT" | "READY":
                        self._enter_state('ABORT')
                        self.logger.debug("Coordinator {} sends {} to {}".format(id, "GLOBAL_ABORT", self.all_participants))
                        self.channel.send_to(self.all_participants, GLOBAL_ABORT)
                        return ("Coordinator {} terminated in state {} due to {}.".format(id, self.state, "GLOBAL_ABORT"))
                    case "PRECOMMIT":
                        self._enter_state('COMMIT')
                        self.logger.debug("Coordinator {} sends {} to {}".format(id, "GLOBAL_COMMIT", self.all_participants))
                        self.channel.send_to(self.all_participants, GLOBAL_COMMIT)
                        return ("Coordinator {} terminated in state {} due to {}.".format(id, self.state, "GLOBAL_COMMIT"))
            else:
                msg = self.channel.receive_from(self.coordinator, CLIENT_TIMEOUT)
                if(not msg):
                    self.logger.warning("Participant {} did not receive a message from the new coordinator.".format(id))
                    self.determineCoordinator()
                    return
                self.logger.debug("Participant {} received state {} from Coordinator {}.".format(id, msg[1], self.coordinator))
                
                match msg[1]:
                    case "READY" | "INIT":
                            self.logger.debug("Participant {} sends {} to coordinator.".format(id, VALID_STATE))
                            self.channel.send_to(self.coordinator, VALID_STATE)
                    case "PRECOMMIT":
                        if self.state == "INIT":
                            self._enter_state('PRECOMMIT')
                            self.logger.debug("Participant {} sends {} to coordinator.".format(id, ADOPTED_STATE))
                            self.channel.send_to(self.coordinator, ADOPTED_STATE)
                        else: 
                            self.logger.debug("Participant {} sends {} to coordinator.".format(id, VALID_STATE))
                            self.channel.send_to(self.coordinator, VALID_STATE)
                    
                    case "COMMIT":
                        if self.state != "COMMIT":
                            self._enter_state('COMMIT')
                        return ("Participant {} terminated in state {} due to {}.".format(self.participant, self.state, "GLOBAL_COMMIT"))
                        
                    case "ABORT":
                        if self.state != "ABORT":
                            self._enter_state('ABORT')
                        return ("Participant {} terminated in state {} due to {}.".format(self.participant, self.state, "GLOBAL_ABORT"))
                    
                msg = self.channel.receive_from(self.coordinator, CLIENT_TIMEOUT)
                if(msg[1]==GLOBAL_COMMIT):
                    self._enter_state('COMMIT')
                    return ( "Participant {} terminated in state {} due to {}.".format(
                        self.participant, self.state, "GLOBAL_COMMIT"))
                else:
                    self._enter_state('ABORT')
                    return ( "Participant {} terminated in state {} due to {}.".format(
                        self.participant, self.state, "GLOBAL_ABORT"))
                    
                        
      
      
  
#region ignore for now 
    # def determineCoordinator(self):
    #         min = 1000000
    #         id = self.participant
    #         for participant in self.all_participants:
    #             if int(participant) < int(min) and participant.state != "INIT":
    #                 min = participant
    #         self.logger.info("Participant {}: Old coordinator was {}.".format(id, self.coordinator))
    #         self.coordinator={min}
    #         self.logger.info("Participant {}: New coordinator is {}.".format(id, self.coordinator))
    #         self.all_participants.remove(min)
    #         if self.coordinator == {id}:
    #             match self.state:
    #                 case "ABORT" | "COMMIT":
    #                     self.logger.debug("Coordinator {} sends {} to {}".format(id, self.state, self.all_participants))
    #                 case "WAIT":
    #                     self._enter_state('ABORT')
    #                     self.logger.debug("Coordinator {} sends {} to {}".format(id, "GLOBAL_ABORT", self.all_participants))
    #                     self.channel.send_to(self.all_participants, GLOBAL_ABORT)
    #                 case "PRECOMMIT": 
    #                     self._enter_state('COMMIT')
    #                     self.logger.debug("Coordinator {} sends {} to {}".format(id, "GLOBAL_COMMIT", self.all_participants))
    #                     self.channel.send_to(self.all_participants, GLOBAL_COMMIT)                    
    #             self.logger.info("Coordinator {} terminated in state {} after the origional coordinator terminated.".format(id, self.state))
    #         else:
    #             msg = self.channel.receive_from(self.coordinator, CLIENT_TIMEOUT)
    #             if(not msg):
    #                 self.logger.warning("Participant {} did not receive a message from the new coordinator.".format(id))
    #                 self.determineCoordinator()
    #                 return
    #             self.logger.debug("Participant {} received state {} from Coordinator {}.".format(id, msg[1], self.coordinator))
    #             match msg[1]:
    #                 case "INIT":
                        
                
                
                
                
    #             if msg[1]=="INIT":
    #                 self.channel.send_to(self.coordinator, VOTE_COMMIT)
    #                 self.logger.debug("Participant {} send {} to coordinator.".format(id, VOTE_COMMIT))
    #                 print("init send")
    #             elif msg[1]=="READY":
    #                 self.channel.send_to(self.coordinator, VOTE_COMMIT)
    #                 print("wait send")
    #             elif msg[1]=="ABORT":
    #                 self.channel.send_to(self.coordinator, VOTE_ABORT)
    #                 print("abort send")
    #             else:
    #                 print("STATE of Coordinator not INIT, WAIT or ABORT, new State: " + msg[1])

    #             msg = self.channel.receive_from(self.coordinator, 5)
    #             if(msg[1]==GLOBAL_COMMIT):
    #                 self._enter_state('COMMIT')
    #                 print( "Participant {} terminated in state {} due to {}.".format(
    #                     self.participant, self.state, "GLOBAL_COMMIT"))
    #             else:
    #                 self._enter_state('ABORT')
    #                 print( "Participant {} terminated in state {} due to {}.".format(
    #                     self.participant, self.state, "GLOBAL_ABORT"))
#endregion