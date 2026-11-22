import pytest
from src.rate_limit import wait_for_slot


def test_spacing_is_shared_between_calls_and_providers_are_separate(tmp_path):
    now=[100.0]
    def sleep(seconds):now[0]+=seconds
    path=tmp_path/'rate.sqlite'
    assert wait_for_slot(path,'mistral',2,30,lambda:now[0],sleep)==0
    assert wait_for_slot(path,'mistral',2,30,lambda:now[0],sleep)==2
    assert now[0]==102
    assert wait_for_slot(path,'outro',2,30,lambda:now[0],sleep)==0


def test_wait_cannot_spend_more_than_deadline(tmp_path):
    path=tmp_path/'rate.sqlite'
    wait_for_slot(path,'mistral',10,30,lambda:100,lambda _:None)
    with pytest.raises(TimeoutError):
        wait_for_slot(path,'mistral',10,5,lambda:100,lambda _:pytest.fail('Não pode esperar'))
    assert wait_for_slot(path,'mistral',10,30,lambda:100,lambda _:None)==10
    with pytest.raises(ValueError):wait_for_slot(path,'mistral',61,30)
