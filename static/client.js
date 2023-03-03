var app = angular.module('video', []);

app.controller('video_query', ($scope, $http)=>{
    $scope.playState = 0;


    $scope.search = ()=>{
        console.log("alolasdaaaaaaaaaaaaaaaaaaaaaaaaaaaa");
        $http({
            method: 'POST',
            url: '/segments',
            data: {
                'names': $scope.names_search?$scope.names_search.split(','):[],
                'time_ranges': [$scope.time_search_start?$scope.time_search_start:0, $scope.time_search_end?$scope.time_search_end:0]
            }
        }).then((res)=>{
            let segments = res.data;
            for(let seg of $scope.segments){
                seg.cover = 'data:image/jpeg;base64,'+ seg.cover;
            }
            $scope.segments = segments;
        },(err)=>{
            console.log(err);
        });
    }


    $scope.query = ()=>{
        console.log($scope.cols);
        console.log($scope.command);
        $http({
            method: 'GET',
            url: '/query?command='+$scope.command.trim()+"&cols="+$scope.cols.trim(),
            data: $scope.command
        }).then((res)=>{
            $scope.results = res.data;
            if($scope.results.length>0){
                $scope.src = 'data:image/jpeg;base64,'+$scope.results[0].frame;
                $scope.index = 0;
            }
        }, (err)=>{
            console.log(err);
        });
    }

    $scope.next = ()=>{
        $scope.index += 1;
        if($scope.index>=$scope.results.length)
            $scope.index = 0;
        $scope.src = 'data:image/jpeg;base64,'+$scope.results[$scope.index].frame;
     
    }

    $scope.prev = ()=>{
        $scope.index -= 1;
        if($scope.index < 0)
            $scope.index = $scope.results.length-1;
        $scope.src = 'data:image/jpeg;base64,'+$scope.results[$scope.index].frame;
    }

    $scope.play = ()=>{
        if($scope.playState == 0){
            setInterval(()=>{
                $scope.next();
                
            }, 300)
        }
    }
});