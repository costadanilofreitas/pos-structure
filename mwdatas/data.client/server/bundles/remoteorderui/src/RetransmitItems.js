import React from 'react';

const maxLines = 14;

function RetransmitItems(props) {
    let groups = [];
    let currentGroup = [];

    let lineNumber = 1;
    for(let item of props.items.data) {
        currentGroup = renderGroups(lineNumber, item, groups, currentGroup, maxLines, 0);
        lineNumber++;
    }
    if(currentGroup.length > 0) {
        let emptyCount = 0;
        while(currentGroup.length < maxLines) {
            currentGroup.push( (<div key={emptyCount++}>&nbsp;</div>) )
        }
        groups.push(currentGroup);
    }

    if(props.smallSize) {
        groups = groups.slice(0, 1);
    } else if(groups.length > 4) {
        groups = groups.slice(0, 4);
    }

    let groupClassName = "col-xs-12";
    if (groups.length === 2) {
        groupClassName = "col-xs-6";
    } else if (groups.length === 3) {
        groupClassName = "col-xs-4";
    } else if (groups.length > 3) {
        groupClassName = "col-xs-3";
    }

    let currentGroupKey = 0;
    return (
        <div className="row">
            {groups.map(group =>
                <div key={currentGroupKey++} className={groupClassName}>
                    {group.map(item => item)}
                </div>
            )}
        </div>)
}

function renderGroups(lineNumber, item, groups, currentGroup, maxItems, currentLevel) {
    let nextLevel = currentLevel;
    if(item.product.type !== "Option") {
        let padding = "";
        for(let i = 0; i < currentLevel; i++) {
            padding += '\u00A0\u00A0';
        }

        if(item.product.currentQty > 0) {
            currentGroup.push((
                <div key={lineNumber + "-" + item.product.partCode}>{padding + (item.product.currentQty) + '\u00A0' + item.product.name}</div>));
        } else {
            currentGroup.push((
                <div className="striked" key={lineNumber + "-" + item.product.partCode}>{padding + item.product.name}</div>));
        }
        nextLevel++;
    }

    if(currentGroup.length === maxItems) {
        groups.push(currentGroup);
        currentGroup = []
    }

    for(let son of item.sons) {
        currentGroup = renderGroups(lineNumber, son, groups, currentGroup, maxItems, nextLevel);

        if(currentGroup.length === maxItems) {
            groups.push(currentGroup);
            currentGroup = []
        }
    }

    return currentGroup;
}

function calculateLines(item) {
    let currentCount = 0;

    if(item.product.type !== "Option") {
        currentCount++;
    }
    for(let son of item.sons) {
        currentCount += calculateLines(son);
    }

    return currentCount;
}

function calculateColumns(order) {
    let numberOfLines = 0;
    for(let item of order.items.data) {
        numberOfLines += calculateLines(item);
    }

    let numberOfColumns = parseInt(numberOfLines / maxLines, 10);
    if(numberOfLines % maxLines > 0) {
        numberOfColumns++;
    }

    if(numberOfColumns > 4) {
        return 4;
    } else {
        return numberOfColumns;
    }
}

function calculateRows(order) {
    let columns = calculateColumns(order);
    return columns / maxLines;
}

export {RetransmitItems, calculateColumns, calculateRows};
