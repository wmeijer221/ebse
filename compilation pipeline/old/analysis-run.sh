# #!/bin/bash
# DESCRIPTION:  Pulls a number of repositories, performs SonarQube analysis on them, 
#               exports the results and finally, the accompanying python script
#               is executed. This script cleans up after itself, meaning that only the 
#               final data set remains after (correct) execution. 
#               Note: Running this script takes a while.
# PREREQS:      Java (11) install (if it fails anyways, check out the apache build guide)
#               SonarQube server must be running (using the Docker image is the easiest)
#               The credentials used in this script should match your SonarQube instance's
# AUTHORS:      W. Meijer
#               L. Visscher 
#               N. Dijkema
# DATE:         08-02-2022


# SonarQube credentials
SONARQUBE_USER=admin
SONARQUBE_PASSWORD=password
SONARQUBE_URI=localhost:9000

while IFS= read -r proj; do
    echo "started with $proj!"

    proj_name=`echo "$proj" | sed 's|/|_|g'`
    proj_name=`echo "$proj_name" | sed 's|\.|-|g'`

    # create new project in sonarqube
    curl -X POST -u $SONARQUBE_USER:$SONARQUBE_PASSWORD -d name=$proj_name -d project=$proj_name -d visibility=public $SONARQUBE_URI/api/projects/create
    curl -X POST -u $SONARQUBE_USER:$SONARQUBE_PASSWORD -d name=$proj_name $SONARQUBE_URI/api/user_tokens/generate

    # TODO: Extract the acquired key
    ACCESS_KEY=18841fee2c0f3619889ba8094a0798abb75ad6a3

    # clone git project and analyze with SonarQube
    # and selects its directory.
    git clone $proj

    # grabs the folderr to which the 
    # repository will be cloned. 
    readarray -d '/' -t slices <<<$proj
    for slice in ${slices[@]} 
    do : 
        repo_dir=$slice 
    done 

    # makes build and runs sonar-scanner
    cd $repo_dir
    mvn clean install -e -Pfastinstall -DskipTests -DskipShade
    
    # adds sonarqube properties
    touch ./sonarqube.properties
    echo "sonar.java.binaries=./target" >> ./sonarqube.properties

    cd .. 

    # mvn clean verify sonar:sonar -Dsonar.projectKey=$proj_name -Dsonar.host.url=$SONARQUBE_URI -Dsonar.login=$ACCESS_KEY

    # removes git directory after its used.
    # rm -r $repo_dir
done < ./repositories.dat
