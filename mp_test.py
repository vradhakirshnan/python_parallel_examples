#!env/bin/python

from multiprocessing import Process

from pprint import pprint
import redis
from dotenv import load_dotenv
import os

def get_env(_env_variable:str)-> str:
    """
    """
    if _env_variable in os.environ:
        pass
    else:
        #BY DEFAULT LOADS .env FILE
        load_dotenv()
        if _env_variable in os.environ:
            pass
        else:
            raise Exception(f'Environment Variable {_env_variable} not set')
    return os.environ[_env_variable]


class RedisSubscriber:
    """
    """

    def __init__(self, stream_name, process_name):
        """
        """
        self.url = get_env('REDIS_ENDPOINT')
        self.pwd = get_env('REDIS_PWD')
        self.connected = False
        self.redis_db = None
        self.stream_name = stream_name
        self.process_name = process_name

    def connect_to_stream(self):
        """
        """
        if self.connected:
            return
        try:
            self.redis_db = redis.Redis(host=self.url, port=6379, charset = 'utf-8', 
                                                password = self.pwd, decode_responses=True)
        except Exception as ex:
            self.connected = False
            raise Exception(f'Unable to connect to {self.url}')
        self.sub = self.redis_db.pubsub()
        self.sub.subscribe(self.stream_name)
        while True:
            for message in self.sub.listen():
                if message is not None:
                    print(f'Stream : {self.stream_name}')
                    print(f'Stream : {self.process_name}')
                    pprint(message)


def get_ticks(_stream, _process):
    """
    """
    red_con = RedisSubscriber(_stream, _process)
    red_con.connect_to_stream()




if __name__ == '__main__':
    print('works')
    #red = RedisSubscriber('niftytick', 'Process-1')
    p1 = Process(target= get_ticks, args=('niftytick', 'Process-1'))
    p1.start()
    #red = RedisSubscriber('niftytick', 'Process-2')
    p2 = Process(target= get_ticks, args=('niftytick', 'Process-2'))
    p2.start()

