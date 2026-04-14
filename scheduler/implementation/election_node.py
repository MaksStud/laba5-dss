import uuid
from typing import List, Optional

from scheduler.abstract.abstract_node import AbstractNode
from scheduler.core.action import Action
from scheduler.core.mailbox import Mailbox
from scheduler.core.node_response import NodeResponse


class ElectionNode(AbstractNode):

    def __init__(self, node_id: uuid.UUID, neighbors: List[uuid.UUID]):
        self.node_id = node_id
        self.mailbox = Mailbox()
        self.neighbors = neighbors

        self.best_initiator_id: Optional[uuid.UUID] = None
        self.parent: Optional[uuid.UUID] = None
        self.responses_expected = 0
        self.responses_received = 0
        self.is_leader = False

    def process_action(self, message: Action) -> NodeResponse:
        data = message.data
        msg_type = data.get('type')

        if msg_type == 'start_election':
            return self._handle_start_election()
        elif msg_type == 'explorer':
            return self._handle_explorer(data['initiator_id'], data['sender_id'])
        elif msg_type == 'echo':
            return self._handle_echo(data['initiator_id'], data['sender_id'])

        return NodeResponse([])

    def _handle_start_election(self) -> NodeResponse:
        if self.best_initiator_id is None or self.node_id < self.best_initiator_id:
            print(f"Node {self.node_id} SPONTANEOUSLY starts wave {self.node_id}")
            return self._start_wave(self.node_id)
        return NodeResponse([])

    def _start_wave(self, initiator_id: uuid.UUID, parent: Optional[uuid.UUID] = None) -> NodeResponse:
        self.best_initiator_id = initiator_id
        self.parent = parent
        self.responses_received = 0

        targets = [n for n in self.neighbors if n != parent]
        self.responses_expected = len(targets)

        actions = []
        for target in targets:
            actions.append(Action(
                data={'type': 'explorer', 'initiator_id': initiator_id, 'sender_id': self.node_id},
                node_id=target,
                action_id=uuid.uuid4()
            ))

        if self.responses_expected == 0:
            if self.parent:
                print(f"Node {self.node_id} (wave {initiator_id}) has no more neighbors, echoing to parent {self.parent}")
                return NodeResponse([Action(
                    data={'type': 'echo', 'initiator_id': initiator_id, 'sender_id': self.node_id},
                    node_id=self.parent,
                    action_id=uuid.uuid4()
                )])
            else:
                self.is_leader = True
                print(f"Node {self.node_id} DECIDED as LEADER (alone)")

        return NodeResponse(actions)

    def _handle_explorer(self, initiator_id: uuid.UUID, sender_id: uuid.UUID) -> NodeResponse:
        if self.best_initiator_id is None or initiator_id < self.best_initiator_id:
            print(f"Node {self.node_id} adopts wave {initiator_id} from {sender_id} (old: {self.best_initiator_id})")
            return self._start_wave(initiator_id, sender_id)

        elif initiator_id == self.best_initiator_id:
            print(f"Node {self.node_id} (wave {initiator_id}) received redundant explorer from {sender_id}, echoing")
            return NodeResponse([Action(
                data={'type': 'echo', 'initiator_id': initiator_id, 'sender_id': self.node_id},
                node_id=sender_id,
                action_id=uuid.uuid4()
            )])

        else:
            print(f"Node {self.node_id} EXTINGUISHES wave {initiator_id} from {sender_id} (current: {self.best_initiator_id})")
            return NodeResponse([])

    def _handle_echo(self, initiator_id: uuid.UUID, sender_id: uuid.UUID) -> NodeResponse:
        if initiator_id != self.best_initiator_id:
            print(f"Node {self.node_id} ignores echo for old wave {initiator_id} (current: {self.best_initiator_id})")
            return NodeResponse([])

        self.responses_received += 1
        print(f"Node {self.node_id} received echo for wave {initiator_id} ({self.responses_received}/{self.responses_expected})")

        if self.responses_received == self.responses_expected:
            if self.parent:
                print(f"Node {self.node_id} (wave {initiator_id}) received all echoes, echoing to parent {self.parent}")
                return NodeResponse([Action(
                    data={'type': 'echo', 'initiator_id': initiator_id, 'sender_id': self.node_id},
                    node_id=self.parent,
                    action_id=uuid.uuid4()
                )])
            else:
                self.is_leader = True
                print(f"\n*** Node {self.node_id} DECIDED as LEADER for wave {initiator_id} ***\n")

        return NodeResponse([])
