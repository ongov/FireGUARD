/*!
 * Chart.js v2.9.3
 * https://www.chartjs.org
 * (c) 2019 Chart.js Contributors
 * Released under the MIT License
 */

var WIND_COLOURS = [
	'#99ebff',
	'#66ff66',
	'#ffff1a',
	'#ff6600',
	'#e60000'
	];
var WIND_LABELS = ['0-5', '5-10', '10-15', '15-20', '20+'];

var helpers$1 = Chart.helpers;

Chart.elements.StackedArc = Chart.Element.extend({
	_type: 'stackedArc',

	inLabelRange: function(mouseX) {
		var vm = this._view;

		if (vm) {
			return (Math.pow(mouseX - vm.x, 2) < Math.pow(vm.radius + vm.hoverRadius, 2));
		}
		return false;
	},

	inRange: function(chartX, chartY) {
		var vm = this._view;

		if (vm) {
			var pointRelativePosition = Chart.helpers.getAngleFromPoint(vm, {x: chartX, y: chartY});
			var angle = pointRelativePosition.angle;
			var distance = pointRelativePosition.distance;

			// Sanitise angle range
			var startAngle = vm.startAngle;
			var endAngle = vm.endAngle;
			while (endAngle < startAngle) {
				endAngle += Chart.TAU;
			}
			while (angle > endAngle) {
				angle -= Chart.TAU;
			}
			while (angle < startAngle) {
				angle += Chart.TAU;
			}

			// Check if within the range of the open/close angle
			var betweenAngles = (angle >= startAngle && angle <= endAngle);
			var withinRadius = (distance >= vm.innerRadius && distance <= vm.outerRadius);

			return (betweenAngles && withinRadius);
		}
		return false;
	},

	getCenterPoint: function() {
		var vm = this._view;
		var halfAngle = (vm.startAngle + vm.endAngle) / 2;
		var halfRadius = (vm.innerRadius + vm.outerRadius) / 2;
		return {
			x: vm.x + Math.cos(halfAngle) * halfRadius,
			y: vm.y + Math.sin(halfAngle) * halfRadius
		};
	},

	getArea: function() {
		var vm = this._view;
		return Math.PI * ((vm.endAngle - vm.startAngle) / (2 * Math.PI)) * (Math.pow(vm.outerRadius, 2) - Math.pow(vm.innerRadius, 2));
	},

	tooltipPosition: function() {
		var vm = this._view;
		var centreAngle = vm.startAngle + ((vm.endAngle - vm.startAngle) / 2);
		var rangeFromCentre = (vm.outerRadius - vm.innerRadius) / 2 + vm.innerRadius;

		return {
			x: vm.x + (Math.cos(centreAngle) * rangeFromCentre),
			y: vm.y + (Math.sin(centreAngle) * rangeFromCentre)
		};
	},

	draw: function() {
		var ctx = this._chart.ctx;
		var vm = this._view;
		var pixelMargin = (vm.borderAlign === 'inner') ? 0.33 : 0;
		var arc = {
			x: vm.x,
			y: vm.y,
			innerRadius: vm.innerRadius,
			outerRadius: Math.max(vm.outerRadius - pixelMargin, 0),
			pixelMargin: pixelMargin,
			startAngle: vm.startAngle,
			endAngle: vm.endAngle,
			fullCircles: Math.floor(vm.circumference / Chart.TAU)
		};
		var i;

		ctx.save();

		//~ if (arc.fullCircles) {
			//~ arc.endAngle = arc.startAngle + Chart.TAU;
			//~ ctx.beginPath();
			//~ ctx.arc(arc.x, arc.y, arc.outerRadius, arc.startAngle, arc.endAngle);
			//~ ctx.arc(arc.x, arc.y, arc.innerRadius, arc.endAngle, arc.startAngle, true);
			//~ ctx.closePath();
			//~ for (i = 0; i < arc.fullCircles; ++i) {
				//~ ctx.fill();
			//~ }
			//~ arc.endAngle = arc.startAngle + vm.circumference % Chart.TAU;
		//~ }
        var padding = (2 * Math.PI / 180);
        for (var i = 0; i < vm.radii.length - 1; i++)
        {
            ctx.fillStyle = WIND_COLOURS[i];
            ctx.strokeStyle = WIND_COLOURS[i];
            ctx.beginPath();
            //~ ctx.arc(arc.x, arc.y, arc.outerRadius, arc.startAngle, arc.endAngle);
            //~ ctx.arc(arc.x, arc.y, arc.innerRadius, arc.endAngle, arc.startAngle, true);
            ctx.arc(arc.x, arc.y, vm.radii[i + 1], arc.startAngle + padding, arc.endAngle - padding);
            ctx.arc(arc.x, arc.y, vm.radii[i], arc.endAngle - padding, arc.startAngle + padding, true);
            ctx.closePath();
            ctx.fill();
            //~ if (vm.borderWidth) {
                //~ ctx.fillStyle = '#000000';
                //~ ctx.strokeStyle = '#000000';
                //~ ctx.lineWidth = 1;
                //~ ctx.beginPath();
                //~ ctx.arc(arc.x, arc.y, vm.radii[i + 1], arc.startAngle, arc.endAngle);
                //~ ctx.arc(arc.x, arc.y, vm.radii[i], arc.endAngle, arc.startAngle, true);
                //~ ctx.closePath();
                //~ ctx.stroke();
            //~ }
        }

		ctx.restore();
	}
});

Chart.defaults.windRose = {};
for (var i in Object.keys(Chart.defaults.polarArea))
{
    var key = Object.keys(Chart.defaults.polarArea)[i];
    Chart.defaults.windRose[key] = Chart.defaults.polarArea[key];
}
// HACK: center wind rose on the value it represents
Chart.defaults.windRose['startAngle'] = (-22.5 / 2) * (Math.PI / 180) -0.5 * Math.PI;
Chart.defaults.windRose['legendCallback'] = function(chart) {
		var list = document.createElement('ul');
		var data = chart.data;
		var datasets = data.datasets;
		var labels = data.labels;
		var i, ilen, listItem, listItemSpan;

		list.setAttribute('class', chart.id + '-legend');
		if (datasets.length) {
			for (i = 0, ilen = datasets[0].data.length; i < ilen; ++i) {
				listItem = list.appendChild(document.createElement('li'));
				listItemSpan = listItem.appendChild(document.createElement('span'));
				listItemSpan.style.backgroundColor = datasets[0].backgroundColor[i];
				if (labels[i]) {
					listItem.appendChild(document.createTextNode(labels[i]));
				}
			}
		}

		return list.outerHTML;
	};
Chart.defaults.windRose['legend'] = {
		labels: {
			generateLabels: function(chart) {
				var data = chart.data;
                return WIND_LABELS.map(function(label, i) {
                    var meta = chart.getDatasetMeta(0);
                    var style = meta.controller.getStyle(i);

                    return {
                        text: label,
                        fillStyle: WIND_COLOURS[i],
                        strokeStyle: WIND_COLOURS[i],
                        lineWidth: style.borderWidth,
                        hidden: false,

                        // Extra data used for toggling the correct item
                        index: i
                    };
                });
				return [];
			}
		}
};
Chart.defaults.windRose['onClick'] = function(e, legendItem) {
			var index = legendItem.index;
			var chart = this.chart;
			var i, ilen, meta;

			for (i = 0, ilen = (chart.data.datasets || []).length; i < ilen; ++i) {
				meta = chart.getDatasetMeta(i);
				meta.data[index].hidden = !meta.data[index].hidden;
			}

			chart.update();
		};

Chart.controllers.windRose = Chart.DatasetController.extend({
	dataElementType: Chart.elements.StackedArc,

	linkScales: Chart.helpers.noop,

	/**
	 * @private
	 */
	_dataElementOptions: [
		'backgroundColor',
		'borderColor',
		'borderWidth',
		'borderAlign',
		'hoverBackgroundColor',
		'hoverBorderColor',
		'hoverBorderWidth',
	],

	/**
	 * @private
	 */
	_getIndexScaleId: function() {
		return this.chart.scale.id;
	},

	/**
	 * @private
	 */
	_getValueScaleId: function() {
		return this.chart.scale.id;
	},

	update: function(reset) {
		var me = this;
		var dataset = me.getDataset();
		var meta = me.getMeta();
		var start = me.chart.options.startAngle || 0;
		var starts = me._starts = [];
		var angles = me._angles = [];
		var arcs = meta.data;
		var i, ilen, angle;

		me._updateRadius();

		meta.count = me.countVisibleElements();

		for (i = 0, ilen = dataset.data.length; i < ilen; i++) {
			starts[i] = start;
			angle = me._computeAngle(i);
			angles[i] = angle;
			start += angle;
		}

		for (i = 0, ilen = arcs.length; i < ilen; ++i) {
			arcs[i]._options = me._resolveDataElementOptions(arcs[i], i);
			me.updateElement(arcs[i], i, reset);
		}
	},

	/**
	 * @private
	 */
	_updateRadius: function() {
		var me = this;
		var chart = me.chart;
		var chartArea = chart.chartArea;
		var opts = chart.options;
		var minSize = Math.min(chartArea.right - chartArea.left, chartArea.bottom - chartArea.top);

		chart.outerRadius = Math.max(minSize / 2, 0);
		chart.innerRadius = Math.max(opts.cutoutPercentage ? (chart.outerRadius / 100) * (opts.cutoutPercentage) : 1, 0);
		chart.radiusLength = (chart.outerRadius - chart.innerRadius) / chart.getVisibleDatasetCount();

		me.outerRadius = chart.outerRadius - (chart.radiusLength * me.index);
		me.innerRadius = me.outerRadius - chart.radiusLength;
	},

	updateElement: function(arc, index, reset) {
		var me = this;
		var chart = me.chart;
		var dataset = me.getDataset();
		var opts = chart.options;
		var animationOpts = opts.animation;
		var scale = chart.scale;
		var labels = chart.data.labels;

		var centerX = scale.xCenter;
		var centerY = scale.yCenter;
    var total = 0;
    for (var i = 0; i < dataset.data[index].length; i++)
    {
        total += dataset.data[index][i];
    }
    var cur = 0;
    var radii = [0];
    for (var i = 0; i < dataset.data[index].length; i++)
    {
        cur += dataset.data[index][i];
        radii.push(scale.getDistanceFromCenterForValue(cur));
    }
		// var negHalfPI = -0.5 * Math.PI;
		var datasetStartAngle = opts.startAngle;
		var distance = arc.hidden ? 0 : (scale.getDistanceFromCenterForValue(total));
		var startAngle = me._starts[index];
		var endAngle = startAngle + (arc.hidden ? 0 : me._angles[index]);

		var resetRadius = animationOpts.animateScale ? 0 : scale.getDistanceFromCenterForValue(total);
		var options = arc._options || {};

		Chart.helpers.extend(arc, {
			// Utility
			_datasetIndex: me.index,
			_index: index,
			_scale: scale,

			// Desired view properties
			_model: {
				backgroundColor: options.backgroundColor,
				borderColor: options.borderColor,
				borderWidth: options.borderWidth,
				borderAlign: options.borderAlign,
				x: centerX,
				y: centerY,
				innerRadius: radii[0],
                radii: radii,
				outerRadius: reset ? resetRadius : distance,
				startAngle: reset && animationOpts.animateRotate ? datasetStartAngle : startAngle,
				endAngle: reset && animationOpts.animateRotate ? datasetStartAngle : endAngle,
				label: Chart.helpers.valueAtIndexOrDefault(labels, index, labels[index])
			}
		});

		arc.pivot();
	},

	countVisibleElements: function() {
		var dataset = this.getDataset();
		var meta = this.getMeta();
		var count = 0;

		Chart.helpers.each(meta.data, function(element, index) {
			if (!isNaN(dataset.data[index][0]) && !element.hidden) {
				count++;
			}
		});

		return count;
	},

	/**
	 * @protected
	 */
	setHoverStyle: function(arc) {
		var model = arc._model;
		var options = arc._options;
		var getHoverColor = Chart.helpers.getHoverColor;
		var valueOrDefault = Chart.helpers.valueOrDefault;

		arc.$previousStyle = {
			backgroundColor: model.backgroundColor,
			borderColor: model.borderColor,
			borderWidth: model.borderWidth,
		};

		model.backgroundColor = valueOrDefault(options.hoverBackgroundColor, getHoverColor(options.backgroundColor));
		model.borderColor = valueOrDefault(options.hoverBorderColor, getHoverColor(options.borderColor));
		model.borderWidth = valueOrDefault(options.hoverBorderWidth, options.borderWidth);
	},

	/**
	 * @private
	 */
	_computeAngle: function(index) {
		var me = this;
		var count = this.getMeta().count;
		var dataset = me.getDataset();
		var meta = me.getMeta();

		if (isNaN(dataset.data[index][0]) || meta.data[index].hidden) {
			return 0;
		}

		// Scriptable options
		var context = {
			chart: me.chart,
			dataIndex: index,
			dataset: dataset,
			datasetIndex: me.index
		};

		return Chart.helpers.options.resolve([
			me.chart.options.elements.arc.angle,
			(2 * Math.PI) / count
		], context, index);
	}
});
