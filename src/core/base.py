from src.core.manager import ConversationManager

class BaseAgent:
    def __init__(self, config: dict):
        self.conversation_manager = ConversationManager()
        self.config = config

    def process_query(self, query: str) -> str:
        if not self.conversation_manager.check_rate_limit():
            return "Rate limit exceeded. Please wait."

        self.conversation_manager.add_to_history('user', query)
        response = self._generate_response(query)
        self.conversation_manager.add_to_history('assistant', response)
        
        self.conversation_manager.store_interaction({
            'query': query,
            'response': response
        })
        
        return response

    def _generate_response(self, query: str) -> str:
        """To be implemented by specific agents"""
        raise NotImplementedError