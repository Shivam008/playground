init: setup vm provision

setup:
	./bin/generate_inventory
	./bin/generate_ssh_config

vm:
	vagrant up

provision:
	ansible-playbook -i inventory/vagrant playbooks/provision.yml

build-regitstration:
	ansible-playbook -i inventory/vagrant playbooks/build-gimb.yml

build-frontend:
	ansible-playbook -i inventory/vagrant playbooks/build-thrak.yml

run-regitstration:
	ansible-playbook -i inventory/vagrant playbooks/run-gimb.yml

run-frontend:
	ansible-playbook -i inventory/vagrant playbooks/run-thrak.yml

debug:
	ansible-playbook -i inventory/vagrant playbooks/debug.yml

clean:
	vagrant destroy
	rm -rf ansible.cfg ssh.config
