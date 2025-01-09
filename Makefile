##------------------------------------------------------------------------------------------
##   The following rules are available:
##	help     		- This text
##	develop			- Run the container in development mode
##	production		- Run the container in production mode
##	buildout		- Run the internal grok installer/configuration (buildout) 
##	runtime    		- Creates a persistent server runtime environment
##	password    	- Prompts for user information, and generates xml that describes a user
##	clean			- Remove the runtime (destroys persistent store and database)
##------------------------------------------------------------------------------------------

help:
	sed -ne '/@sed/!s/^##//p' $(MAKEFILE_LIST)

areyousure:
	@echo "This will remove the persistent database and all runtime files for the server (including the source)."
	@( read -p "Are you sure? [Y/N]: " rsp && case "$$rsp" in [yY]) true;; *) false;; esac )

runtime:
	bin/runtime

develop: runtime
	bin/run debug

production: runtime
	bin/run deploy

buildout:
	bin/buildout

password:
	bin/zpasswd

clean: areyousure
	rm -rf runtime
