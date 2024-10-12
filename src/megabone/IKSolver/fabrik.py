import math

from PyQt5.QtCore import QPointF

class FABRIK:
    def __init__(self, bones):
        self.bones = bones
        self.lengths = []
        self.total_length = 0

        # Calculate and store the original bone lengths
        for bone in bones:
            length = bone.calculateLength()
            self.lengths.append(length)
            self.total_length += length

        # Store original bone positions for constraints
        self.original_angles = [bone.calculateAngle() for bone in bones]

    # TODO manage pole vector
    def solve(self, target_pos, iterations=10):
        if not self.bones:
            return

        # Get chain points
        points = [self.bones[0].start_point]
        for bone in self.bones:
            points.append(bone.end_point)
        points = [QPointF(p.x(), p.y()) for p in points]

        # Check if target is reachable
        base_to_target = math.sqrt(
            (target_pos.x() - points[0].x()) ** 2
            + (target_pos.y() - points[0].y()) ** 2
        )

        if base_to_target > self.total_length:
            # Target is too far - stretch towards it
            direction = QPointF(
                target_pos.x() - points[0].x(), target_pos.y() - points[0].y()
            )
            length = math.sqrt(direction.x() ** 2 + direction.y() ** 2)
            direction = QPointF(
                direction.x() / length * self.total_length,
                direction.y() / length * self.total_length,
            )
            target_pos = QPointF(
                points[0].x() + direction.x(), points[0].y() + direction.y()
            )

        for _ in range(iterations):
            # Forward reaching: Set end effector to target
            points[-1] = QPointF(target_pos.x(), target_pos.y())

            # Backward reaching: Update points from end to start
            for i in range(len(points) - 2, -1, -1):
                current = points[i + 1]
                next_point = points[i]

                # Get direction vector
                direction = QPointF(
                    next_point.x() - current.x(), next_point.y() - current.y()
                )

                # Normalize and scale by bone length
                length = math.sqrt(direction.x() ** 2 + direction.y() ** 2)
                if length > 0:
                    direction = QPointF(
                        direction.x() / length * self.lengths[i],
                        direction.y() / length * self.lengths[i],
                    )

                # Set new position
                points[i] = QPointF(
                    current.x() + direction.x(), current.y() + direction.y()
                )

            # Forward reaching: Update points from start to end
            points[0] = QPointF(
                self.bones[0].start_point.x(), self.bones[0].start_point.y()
            )

            for i in range(len(points) - 1):
                current = points[i]
                next_point = points[i + 1]

                direction = QPointF(
                    next_point.x() - current.x(), next_point.y() - current.y()
                )

                length = math.sqrt(direction.x() ** 2 + direction.y() ** 2)
                if length > 0:
                    direction = QPointF(
                        direction.x() / length * self.lengths[i],
                        direction.y() / length * self.lengths[i],
                    )

                points[i + 1] = QPointF(
                    current.x() + direction.x(), current.y() + direction.y()
                )

            # Apply angle constraints
            # for i in range(len(self.bones)):
            #     current_angle = math.atan2(
            #         points[i + 1].y() - points[i].y(), points[i + 1].x() - points[i].x()
            #     )

            #     # Example constraint: limit rotation to ±90° from original angle
            #     angle_diff = current_angle - self.original_angles[i]
            #     while angle_diff > math.pi:
            #         angle_diff -= 2 * math.pi
            #     while angle_diff < -math.pi:
            #         angle_diff += 2 * math.pi

            #     max_rotation = math.pi / 2  # 90 degrees
            #     if abs(angle_diff) > max_rotation:
            #         # Clamp the angle
            #         target_angle = self.original_angles[i]
            #         if angle_diff > 0:
            #             target_angle += max_rotation
            #         else:
            #             target_angle -= max_rotation

            #         # Recalculate point position
            #         points[i + 1] = QPointF(
            #             points[i].x() + math.cos(target_angle) * self.lengths[i],
            #             points[i].y() + math.sin(target_angle) * self.lengths[i],
            #         )

        # Update bone positions
        for i, bone in enumerate(self.bones):
            bone.start_point = points[i]
            bone.end_point = points[i + 1]
            bone.update()
            bone.updateChildrenTransform()