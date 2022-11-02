#!/bin/bash
# This script only works if there is exactly one userpool
# It removes all users from that one userpool
number_userpools=$(aws cognito-idp list-user-pools --max-results 2 |
    grep "Id" |
    wc -l)
if test $number_userpools -ne 1
then
    echo This script requires exactly one userpool
    exit 1
fi

userpool=$(aws cognito-idp list-user-pools --max-results 1 |
    grep Id |
    sed 's/ *"Id": "//' |
    sed 's/",//')
echo User pool has ID: $userpool

users=$(aws cognito-idp list-users --user-pool-id $userpool |
    grep Username |
    sed 's/ *"Username": "//' |
    sed 's/",//')

for user in $users; do
  echo Deleting user $user from user pool $userpool
  $(aws cognito-idp admin-delete-user --user-pool-id $userpool --username $user)
done
