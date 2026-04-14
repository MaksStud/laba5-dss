import uuid
from typing import List, Dict

from scheduler.abstract.abstract_network import AbstractNetwork
from scheduler.implementation.election_node import ElectionNode
from scheduler.core.action import Action

class ElectionNetwork(AbstractNetwork):
    NUMBER_OF_NODES = 8

    def __init__(self) -> None:
        self.nodes = []
        ids = [uuid.uuid4() for _ in range(self.NUMBER_OF_NODES)]
        self.__get_edges(ids)
        for node_id in ids:
            node = ElectionNode(node_id, self.edges[node_id])
            # To start the election, we can put a 'start_election' message in the mailbox
            # Let's make everyone an initiator to test extinction
            node.mailbox.add_inbox_action(Action(
                data={'type': 'start_election'},
                node_id=node_id,
                action_id=uuid.uuid4()
            ))
            self.nodes.append(node)
        super().__init__(self.nodes)

    def __get_edges(self, ids: List[uuid.UUID]) -> Dict[uuid.UUID, List[uuid.UUID]]:
        self.edges = {
            ids[0]: [ids[1], ids[2]],
            ids[1]: [ids[0], ids[3], ids[4]],
            ids[2]: [ids[0], ids[5], ids[6], ids[7]],
            ids[3]: [ids[1]],
            ids[4]: [ids[1]],
            ids[5]: [ids[2]],
            ids[6]: [ids[2]],
            ids[7]: [ids[2]]
        }
        return self.edges
