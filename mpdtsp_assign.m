function [ q_solvable, q_rest ] = mpdtsp_assign( v,m,q,Q,Slist, subset, num_subset)
%This function should be called iteratively to solve the mpdtsp assigning
%problem. Each resulting subproblem should be guaranteed solvable. 
%   v -- number of warehouses
%   m -- number of commodity
%   q -- current demand that needs to be assigned
%        q = q_solvable + q_rest

    x = binvar(v,v,'full'); % adjacency matrix
    for i = 1:v,
        x(i,i) = 0;
    end
    q_real = sdpvar(v,m);    
    
    % constraints for adjacency matrix
    constr = [sum(x,1)' == 1; sum(x,2) == 1];
    
    % constraints for q_real so that q_real is element-wise 'no greater than' q 
    constr = [constr; -abs(q)<=q_real<=abs(q); q_real.*sign(q)>=0];
    
    V = 1:v;
    for i = 2:length(subset)-1,
        for j = 1:size(subset{i},1),
            tempS = subset{i}(j,:);
            constr = [constr; sum(sum(x(tempS,setdiff(V,tempS))))>=1]; % additional constraints for TSP settings
        end
    end
    
    % capacity constraints
    for i = 1:size(Slist,1),
       calS = Slist(i,:);
       [cell_idx,row_idx] = find_subset(calS(1),num_subset);
       set = subset{cell_idx}(row_idx,:);
       tempsum = sum(q_real(set , 1));
       for j = 2:length(calS),
           [cell_idx,row_idx] = find_subset(calS(j),num_subset);
           setB = subset{cell_idx}(row_idx,:);
           set = union(set,setB);
           tempsum = tempsum + sum(q_real(setB , j));
       end
       constr = [constr; sum(sum(x(set,:))) >= tempsum/Q];
    end
    
    
    obj = sum(sum(sign(q).*(q-q_real)));
    ops = sdpsettings('verbose',2,'debug',1,'savesolveroutput',1);
    
    % solving information
    relative_gap = 0.0035;
    maxtime = 1800;
    ops.solver = 'xpress';
    ops.xpress.MIPRELSTOP = relative_gap;
    ops.xpress.MAXTIME = maxtime;
    
    solution = optimize(constr,obj,ops);
    
    q_solvable = value(q_real);
    q_solvable = sign(q_solvable).*floor(abs(q_solvable));
    q_rest = q-q_solvable;
    

end

